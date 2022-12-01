Configuration
=============

Hydroplane is configured by passing a configuration YAML file to it with the ``-c/--conf`` flag. By default, Hydroplane will read its configuration from ``basic-config.yml``.

To provide your own configuration file to Hydroplane, write your configuration YAML to a file (e.g. ``conf.yml``) and run Hydroplane like so:

.. code-block:: bash

    bin/hydroplane -c conf.yml

There are two things that need to be configured in settings: Hydroplane's :doc:`runtime<runtimes>` and its :doc:`secret store<secrets>`. Optionally, you can also configure the :ref:`process culler<process culler>`.

Example Configurations
----------------------

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


Here's an example that configures process culling (see :ref:`the process culler documentation<process culler>` for more information on how to configure it):

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


Each runtime has its own specific configuration that's documented in the :doc:`runtimes` section of this documentation.
