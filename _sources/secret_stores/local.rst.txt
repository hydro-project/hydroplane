``local`` Secret Store
======================

Hydroplane needs some form of secret store to safely keep credentials that it uses to communicate
with the backend runtime. We have a local secret store that stores secrets on the local filesystem,
symetrically encrypted with a password. It's not meant for production use, but it should be good
enough for local development and experimentation.


.. autopydantic_model:: hydroplane.secret_stores.local.Settings


Initializing a Local Secret Store
---------------------------------

To initialize your local secret store:

.. code-block:: bash

    poetry run bin/local-secret-store init


You'll be prompted to enter a password for the secret store. By default, it will be initialized in ``~/.hydro_secrets`` but you can change its location by adding the ``--store-location`` flag to the above command.

Using the Local Secret Store
----------------------------

Use the script ``bin/local-secret-store`` to manipulate the local secret store. For details on its usage, run ``bin/local-secret-store --help``.
