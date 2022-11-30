Processes
=========

Hydroplane is responsible for creating and destroying **processes**. In Hydroplane's case, a process is anything that runs inside a single container.

Creating Processes
------------------

When launching a process, you have to provide a **process specification**, or **process spec** for short. A process spec describes the process: it gives the process a name and specifies the location of the process's container image and how the container should be configured.

Here's an example of a simple process spec:

.. code-block:: json

    {
      "process_name": "test",
      "container": {
        "image_uri": "nginxdemos/hello",
        "ports": [
          {
            "container_port": 80,
            "host_port": 9090,
            "protocol": "tcp"
          }
        ]
      }
    }

The process that this process spec describes is named ``test``, and runs the container image `nginxdemos/hello <https://hub.docker.com/r/nginxdemos/hello>`_, which uses ``nginx`` to display a simple webpage.

While most of the process spec is optional, it gives you the ability to change a lot of the details of how your process runs. Here's a detailed description of the process spec:

.. automodule:: hydroplane.models.process_spec
  :members:

.. autopydantic_model:: hydroplane.models.container_spec.ContainerSpec

.. automodule:: hydroplane.models.container_spec
  :members:

Process Groups
~~~~~~~~~~~~~~

A process can optionally be made part of a process **group** when it's created by setting the ``group`` field of the process spec. Hydroplane knows how to list the processes that are part of a group, as well as how to destroy a group of processes all at once.

Public and Private Processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, processes are private. This means that processes can communicate with one another (and, for some runtimes, other services running in that runtime), but cannot communicate with the outside world.

The ``has_public_ip`` field of the process spec controls whether a process is public or private. If it's set to ``true``, the service will be publicly routable, and its public IP address will be provided instead of its private one(s) when it's listed.

Listing Processes
-----------------

The Hydroplane server itself is stateless, but the server can interrogate its runtime to list processes. The way that the runtime is interrogated varies, but usually Hydroplane annotates the resources it manages with tags, and uses those tags to find those processes later.

.. _process culler:

Process Culling
---------------

If you're running experiments in the cloud, running processes cost money, so you want to make sure you don't leave processes sitting around accidentally. Hydroplane has a **process culler** that automatically stops any processes that are older than a certain age (specified in minutes).

The process culler's settings are described below. Here's an example process culler configuration:

.. code-block:: yaml


.. autopydantic_model:: hydroplane.utils.process_culler.Settings
