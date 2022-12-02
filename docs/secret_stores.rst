Secret Stores
=============

Most of Hydroplane's runtimes need access to a secret store in order to retrieve enough credentials to authenticate. For runtimes like ``docker`` that don't require any secrets, the ``none`` secret store can be used.

.. toctree::
   :maxdepth: 1
   :caption: Available Runtimes

   secret_stores/local
   secret_stores/none
