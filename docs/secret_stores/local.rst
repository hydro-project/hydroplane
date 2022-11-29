``local`` Secret Store
======================

Hydroplane needs some form of secret store to safely keep credentials that it uses to communicate
with the backend runtime. We have a local secret store that stores secrets on the local filesystem,
symetrically encrypted with a password. It's not meant for production use, but it should be good
enough for local development and experimentation.

.. contents::

Settings
--------

.. autopydantic_model:: hydroplane.secret_stores.local.Settings


Here's an example configuration that you might see inside of your :doc:`settings file</settings>`:

.. code-block:: yaml

    secret_store:
      secret_store_type: local
      store_location: /Users/alexras/.hydro_secrets


Initializing a Local Secret Store
---------------------------------

To initialize your local secret store:

.. code-block:: bash

    poetry run bin/local-secret-store init


You'll be prompted to enter a password for the secret store. By default, it will be initialized in ``~/.hydro_secrets`` but you can change its location by adding the ``--store-location`` flag to the above command.

Adding a Simple Secret to the Secret Store
----------------------------------------------

To add a secret to the secret store:

.. code-block:: bash

    poetry run bin/local-secret-store add <secret name>


You'll be prompted to enter the password for the secret store, and then prompted to enter the contents of the secret itself.

Adding Longer or More Complex Secrets to the Secret Store
---------------------------------------------------------

Entering a secret from a prompt is useful for secrets like passwords and authentication tokens that aren't very long or complicated. Some secrets are longer or more complex, like a certificate or a private key, and don't lend themselves well to being typed or pasted in at a prompt.

To add the contents of a file as a secret:

.. code-block:: bash

    poetry run bin/local-secret-store add -f <input filename> <secret name>

You'll be prompted to enter the password for the secret store, and the provided input file's contents will be stored in the secret.

Removing a Secret from the Secret Store
---------------------------------------

To remove a secret from the secret store:

.. code-block:: bash

    poetry run bin/local-secret-store remove <secret name>
