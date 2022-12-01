Defining Secrets
================

Both Hydroplane and the processes it creates need access to secret values. Some secret values (**Hydroplane secrets**) are used by Hydroplane to authenticate with the runtime. Other secret values (**process secrets**) are used by processes when they run.

Hydroplane Secrets
------------------

Hydroplane secrets are stored in a **secret store**. Most of Hydroplane's runtimes need access to this secret store in order to retrieve enough credentials to authenticate with the runtime. For runtimes like ``docker`` that don't require any secrets, the ``none`` secret store can be used.

See :doc:`</secret_stores>` for a list of available secret stores and their settings.

.. autopydantic_model:: hydroplane.models.secret.HydroplaneSecret

Secrets can contain any string, even one that contains newlines or other special characters.

Grouping Related Secrets Together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's sometimes convenient to group related credentials together in a single secret; for example, you might want to store a username and password for a service together in a single secret instead of storing them in two separate secrets. To store related credentials together in the same secret, create a secret whose content is a JSON object and use ``HydroplaneSecret``'s optional ``key`` field to refer to different keys within the object. See :ref:`the EKS runtime's authentication setup<eks-secret-example>` for an example of this in action.


Process Secrets
---------------

Process secrets are stored by the runtime itself. You can use process secrets to pass secret values to a process's environment variables or to provide the process with authentication information to a container registry without having to pass those secrets around in cleartext.

Here's an example of using a process secret to retrieve a secret value for an environment variable:

.. code-block:: json

    {
      "process_name": "my-process",
      "container": {
        "image_uri": "foo/bar",
        "ports": [
          {
            "container_port": "80"
          }
        ],
        "env": [
          {
            "name": "ULTRA_SECRET_THINGY",
            "value": {
              "secret_name": "ultra-secret"
            }
          }
        ]
      }
    }


.. autopydantic_model:: hydroplane.models.secret.ProcessSecret
