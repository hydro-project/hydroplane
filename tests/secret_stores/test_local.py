from pathlib import Path
import tempfile

import pytest

from hydroplane.secret_stores.local import LocalSecretStore, Settings

TEST_PASSWORD = 'secret123'


def new_test_store(parent_dir: Path) -> LocalSecretStore:
    secret_store_dir = parent_dir / 'secret_store'

    store = LocalSecretStore(Settings(store_location=secret_store_dir, password=TEST_PASSWORD))

    store.initialize_store()

    return store


def test_add_secret_happy_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        store = new_test_store(tmpdir)

        store.add_secret('my_secret', 'secret contents here')

        assert store.get_secret('my_secret') == 'secret contents here'


def test_missing_store_directory_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        store = LocalSecretStore(
            Settings(store_location=tmpdir / 'bad-path', password=TEST_PASSWORD)
        )

        with pytest.raises(ValueError):
            store.add_secret('my_secret', 'secret contents')


def test_add_existing_secret_raises_unless_overwrite_specified():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        store = new_test_store(tmpdir)

        store.add_secret('my_secret', 'secret contents here')

        with pytest.raises(KeyError):
            store.add_secret('my_secret', 'new secret contents')

        assert store.get_secret('my_secret') == 'secret contents here'

        store.add_secret('my_secret', 'sudo new secret contents', overwrite=True)

        assert store.get_secret('my_secret') == 'sudo new secret contents'


def test_remove_nonexistent_secret_raises():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        store = new_test_store(tmpdir)

        with pytest.raises(KeyError):
            store.remove_secret('missing_secret')


def test_remove_secret_happy_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        store = new_test_store(tmpdir)

        store.add_secret('my_secret', 'secret contents here')
        assert store.get_secret('my_secret') == 'secret contents here'

        store.remove_secret('my_secret')

        with pytest.raises(KeyError):
            store.get_secret('my_secret')
