Defining Processes
==================

Hydroplane is responsible for creating and destroying **processes**. Hydroplane defines a process as anything that runs inside a single container.

Process Specifications
----------------------

When launching a process, you have to provide a **process specification**, or **process spec** for short. A process spec describes the process: it gives the process a name and specifies the location of the process's container image and how the process's container should be configured.

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

This process spec describes a process named ``test`` that runs the container image `nginxdemos/hello <https://hub.docker.com/r/nginxdemos/hello>`_, which uses ``nginx`` to display a simple webpage.

Most of the process spec is optional, but you have the ability to change a lot of the details of how your process runs by changing its process spec. Here's a detailed description of the process spec's format:

.. automodule:: hydroplane.models.process_spec
  :members:

.. autopydantic_model:: hydroplane.models.container_spec.ContainerSpec

.. automodule:: hydroplane.models.container_spec
  :members:

Process Groups
~~~~~~~~~~~~~~

A process can optionally be made part of a process **group** when it's created by setting the ``group`` field of the process spec. Hydroplane knows how to list the processes that are part of a group, as well as how to destroy a group of processes all at once.

Listing Processes
-----------------

The Hydroplane server itself is stateless, but it can interrogate its runtime to list running processes. The way that the runtime is interrogated varies, but usually Hydroplane annotates the resources it manages with tags and uses those tags to distinguish processes it manages from other resources in the runtime.

Public and Private Processes
----------------------------

By default, processes are private, meaning that they can communicate with one another (and often other services running in that runtime) but cannot communicate with the outside world.

The ``has_public_ip`` field of the process spec controls whether a process is public or private. If the field is set to ``true``, the service will be publicly routable, and its public IP address will be provided instead of its private one(s) when it's listed.

.. _process culler:

Process Culling
---------------

If you're running experiments in the cloud, running processes cost money, so you want to make sure you don't leave processes sitting around accidentally. Hydroplane has a **process culler** that automatically stops any processes that are older than a certain age (specified in minutes).

The process culler's settings are described below. Here's an example configuration file showing process culler configuration:

.. code-block:: yaml

    ---
    secret_store:
      secret_store_type: none

    runtime:
      runtime_type: docker

    process_culling:
      # Cull all processes older than two hours
      max_age_minutes: 120

      # Cull processes every 5 minutes
      culling_interval_minutes: 5


.. autopydantic_model:: hydroplane.utils.process_culler.Settings
