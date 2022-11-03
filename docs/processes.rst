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
            "host_port": 9090
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

A process can optionally be made part of a process **group** when it's created. Hydroplane knows how to list the processes that are part of a group, as well as how to destroy a group of processes all at once.
