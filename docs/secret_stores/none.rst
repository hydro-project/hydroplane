``none`` Secret Store
=====================

As the name implies, the ``none`` secret store is a secret store that does nothing. It doesn't store secrets, and if a runtime asks it for a secret, it throws an error. The ``none`` secret store is a nice default if you're using a runtime like :doc:`Docker</runtimes/docker>` that doesn't need any secrets to run.

Settings
--------

.. autopydantic_model:: hydroplane.secret_stores.none.Settings
