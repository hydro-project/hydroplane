import argparse
import base64
import getpass
import hashlib
from pathlib import Path
import logging
import os
import sys
import uuid

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .secret_store import SecretStore

# The default location where the local secret store will store secrets
DEFAULT_SECRET_STORE_LOCATION = os.path.expanduser(Path('~/.hydro_secrets'))

SENTINEL_TEST_PHRASE = "It's a secret to everybody"


class LocalSecretStore(SecretStore):
    """A local, password-protected secret store

    This secret store is meant for (relatively) secure storage of secrets on the local
    filesystem. It encrypts secrets using a symmetric key derived from a password, using the
    mechanism described here: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet

    It has some basic facilities for making sure that everything is encrypted with the same
    password, but doesn't go too much further than that with regard to checking. Needless to say,
    this isn't the sort of thing you'd want to use in production, but for local development and
    experiments, it should be fine.
    """

    def __init__(self, store_location: Path, password: str):
        self.store_location = store_location
        self.password = password

    def _get_fernet(self, validate_sentinel: bool = True) -> Fernet:
        with open(self._salt_path, 'rb') as fp:
            salt = fp.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )

        fernet = Fernet(base64.urlsafe_b64encode(kdf.derive(self.password.encode('utf-8'))))

        # Check sentinel file to make sure the password matches the one
        # that was used to create the store
        if validate_sentinel:
            with open(self._sentinel_path, 'rb') as fp:
                sentinel_matches = False

                try:
                    sentinel_contents = fernet.decrypt(fp.read()).decode('utf-8')
                    sentinel_matches = sentinel_contents.startswith(SENTINEL_TEST_PHRASE)
                except InvalidToken:
                    pass

                if not sentinel_matches:
                    raise ValueError("Provided password doesn't match the one used to create "
                                     f"the store at {self.store_location}")

        return fernet

    def _secret_path(self, secret_name: str) -> Path:
        return self.store_location / hashlib.md5(secret_name.encode('utf-8')).hexdigest()

    @property
    def _sentinel_path(self) -> Path:
        return self.store_location / '.sentinel'

    @property
    def _salt_path(self) -> Path:
        return self.store_location / '.salt'

    def initialize_store(self):
        logging.info(f"Initializing local secret store at {self.store_location}")

        try:
            self.store_location.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            raise ValueError(f'Cannot create secret store at {self.store_location}: '
                             'directory not empty')

        with open(self._salt_path, 'wb') as fp:
            salt = os.urandom(16)

            fp.write(salt)

        with open(self._sentinel_path, 'wb') as fp:
            # Add a random UUID after the passphrase to somewhat randomize its contents
            sentinel_contents = f'{SENTINEL_TEST_PHRASE} {uuid.uuid4().hex}'.encode('utf-8')
            fp.write(self._get_fernet(validate_sentinel=False).encrypt(sentinel_contents))

    def add_secret(self, secret_name: str, secret_data: str, overwrite=False):
        if not self.store_location.exists():
            raise ValueError(f'Secret store not found at {self.store_location}')

        fernet = self._get_fernet()

        secret_file = self._secret_path(secret_name)

        if secret_file.exists() and not overwrite:
            raise KeyError(f"Secret '{secret_name}' already exists")

        logging.info(f'Adding secret {secret_name}')

        with open(self._secret_path(secret_name), 'wb') as fp:
            fp.write(fernet.encrypt(secret_data.encode('utf-8')))

    def get_secret(self, secret_name: str) -> str:
        secret_file = self._secret_path(secret_name)

        if not secret_file.exists():
            raise KeyError(f"Secret '{secret_name}' not found "
                           f"in secret store at {self.store_location}")

        with open(secret_file, 'rb') as fp:
            encrypted_secret = fp.read()

            f = self._get_fernet()
            return f.decrypt(encrypted_secret).decode('utf-8')

    def remove_secret(self, secret_name: str):
        secret_file = self._secret_path(secret_name)

        if not secret_file.exists():
            raise KeyError(f"Secret '{secret_name}' not found "
                           f"in secret store at {self.store_location}")

        logging.info(f'Deleting secret {secret_name}')
        os.remove(secret_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        prog='local-secret-store',
        description='tools for managing a local Hydroplane secret store'
    )
    parser.add_argument('--store_location', type=Path,
                        help='location of the secret store (default %(default)s)',
                        default=DEFAULT_SECRET_STORE_LOCATION)

    subparsers = parser.add_subparsers(help='sub-command help')
    subparsers.required = True

    init_parser = subparsers.add_parser('init', help='initialize a secret store')
    init_parser.set_defaults(func='init')

    add_secret_parser = subparsers.add_parser('add', help='add a secret to the secret store')
    add_secret_parser.add_argument('secret_name', help='the name of the new secret')
    add_secret_parser.add_argument('--overwrite', default=False, action='store_true',
                                   help='overwrite the secret if it already exists')
    add_secret_parser.set_defaults(func='add')

    get_secret_parser = subparsers.add_parser('get', help='read a secret from the secret store')
    get_secret_parser.add_argument('secret_name', help='the name of the secret')
    get_secret_parser.set_defaults(func='get')

    remove_secret_parser = subparsers.add_parser('remove',
                                                 help='remove a secret from the secret store')
    remove_secret_parser.add_argument('secret_name', help='the name of the secret to remove')
    remove_secret_parser.set_defaults(func='remove')

    args = parser.parse_args()

    func = args.func
    store_location = args.store_location

    try:
        if func == 'init':
            password_1 = getpass.getpass('Enter the password for the new secret store: ')
            password_2 = getpass.getpass('Enter the same password again: ')

            if password_1 != password_2:
                logging.fatal("Provided passwords don't match")
                sys.exit(1)

            store = LocalSecretStore(store_location, password_1)

            store.initialize_store()
        else:
            password = getpass.getpass('Enter the password for the secret store: ')
            store = LocalSecretStore(store_location, password)

            if func == 'add':
                secret_data = getpass.getpass('Enter the contents of the secret: ')

                store.add_secret(args.secret_name, secret_data)
            elif func == 'remove':
                store.remove_secret(args.secret_name)
            elif func == 'get':
                print(store.get_secret(args.secret_name))
            else:
                raise ValueError(f'Unknown directive {func}')
    except Exception as e:
        logging.error(f'ERROR: {e}')
