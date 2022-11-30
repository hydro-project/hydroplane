Settings
========

Hydroplane is configured by providing a path to a YAML file in the `CONF` environment variable in the server's environment.

There are two things that need to be configured in settings: Hydroplane's :doc:`runtime<runtimes>` and its :doc:`secret store<secrets>`. Optionally, you can also configure the :ref:`process culler<process culler>`.

Here's a basic example of a configuration file that uses the ``local`` secret store and the ``docker`` runtime:

.. code-block:: yaml

  ---
  secret_store:
    secret_store_type: local
    store_location: ~/.hydro_secrets

  runtime:
    runtime_type: docker

and another example that uses the ``local`` secret store and the ``eks`` runtime:

.. code-block:: yaml

  ---
  secret_store:
    secret_store_type: local
    store_location: ~/.hydro_secrets

  runtime:
    runtime_type: eks
    cluster_name: test-cluster
    region: us-west-2
    credentials:
      access_key:
        access_key_id:
          secret_name: aws-credentials
          key: AccessKeyId
        secret_access_key:
          secret_name: aws-credentials
          key: SecretAccessKey


Each runtime has its own specific configuration that's documented in the :doc:`runtimes` section of this documentation.
