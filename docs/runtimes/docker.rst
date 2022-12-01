``docker`` - Docker (Single-Node) Runtime
=========================================

The single-node `Docker <https://www.docker.com/>`_ runtime is meant to be a simple way to run containers without having to set up a bunch of infrastructure.

Its configuration needs are pretty minimal; you just need a local Docker daemon running.

Containers started by Hydroplane will run in the ``hydroplane`` `bridge network <https://docs.docker.com/network/bridge/>`_, which allows them to use DNS names to refer to one another.

Settings
--------

.. autopydantic_model:: hydroplane.runtimes.docker.Settings

The ``docker`` runtime doesn't have any substantive settings, but you still need to specify it as your runtime for Hydroplane to use it.

Example Configuration
^^^^^^^^^^^^^^^^^^^^^

Here's an example of a configuration file that uses the ``docker`` runtime. Since the ``docker`` runtime doesn't need a secret store, this configuration uses the :doc:`"none" secret store</secret_stores/none>`.

.. code-block:: yaml
    ---
    secret_store:
      secret_store_type: none

    runtime:
      runtime_type: docker

Quickstart
----------

Follow the :doc:`quickstart guide</quickstart>` to get Hydroplane set up to use the ``docker`` runtime.
