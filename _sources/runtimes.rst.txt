Runtimes
========

Hydroplane doesn't run containers by itself. Instead, it communicates with a pre-existing container **runtime** that runs those containers on its behalf. In this way, Hydroplane acts as a common interface to a variety of different container runtimes.

.. toctree::
   :maxdepth: 1
   :caption: Available Runtimes

   runtimes/docker
   runtimes/eks
