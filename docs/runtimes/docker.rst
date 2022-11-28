``docker`` - Docker (Single-Node) Runtime
=========================================

The single-node `Docker <https://www.docker.com/>`_ runtime is meant to be a simple way to run containers without having to set up a bunch of infrastructure.

Its configuration needs are pretty minimal; you just need a local Docker daemon running.

Containers started by Hydroplane will run in the ``hydroplane`` `bridge network <https://docs.docker.com/network/bridge/>`_, which allows them to use DNS names to refer to one another.

.. autopydantic_model:: hydroplane.runtimes.docker.Settings
