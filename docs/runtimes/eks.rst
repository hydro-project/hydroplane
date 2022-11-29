``eks`` - Amazon EKS
====================

The ``eks`` runtime integrates with EKS, AWS's managed Kubernetes offering.

Settings
--------

.. autopydantic_model:: hydroplane.runtimes.eks.Settings

Authenticating with AWS
-----------------------

In order for Hydroplane to launch processes on an EKS cluster, it must be able to authenticate with that cluster. To authenticate, you'll need an AWS `access key ID and corresponding secret access key <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html>`_. These credentials will need to be stored in Hydroplane's :doc:`secret store </secrets>`.

.. _eks-secret-example:

Authenticating with IAM Credentials
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here's an example configuration that uses a secret stored in Hydroplane's secret store to authenticate with EKS. This config uses a secret named ``aws-creds`` that's stored in the secret store as a JSON object like so:

.. code-block:: json

    {"AccessKeyId":"XXXXXXXXX","SecretAccessKey":"XXXXXXX"}

These related credentials are referenced individually using the ``key`` field.

.. code-block:: yaml

    runtime:
        runtime_type: eks
        cluster_name: my-cluster
        region: us-west-2
        credentials:
          access_key:
            access_key_id:
              secret_name: aws-creds
              key: AccessKeyId
            secret_access_key:
              secret_name: aws-creds
              key: SecretAccessKey

Authenticating with Role Assumption
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While nothing stops you from authenticating directly with an access key and secret, it's generally considered a best practice to authenticate using `temporary IAM credentials <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-resources.html#using-temp-creds-sdk-cli>`_. These credentials are associated with a given IAM role, and expire after a certain period of time. Hydroplane will attempt to automatically renew these temporary credentials periodically.

Here's an example of using the ``aws-creds`` secret from above to authenticate and then assume the role ``EKSAdmin``. Most of this configuration will look familiar if you've looked at the configuration in the last section, but we've added an ``assume_role`` block to define the role assumption.

.. code-block:: yaml

    runtime:
        runtime_type: eks
        cluster_name: my-cluster
        region: us-west-2
        credentials:
          access_key:
            access_key_id:
              secret_name: aws-creds
              key: AccessKeyId
            secret_access_key:
              secret_name: aws-creds
              key: SecretAccessKey
           assume_role:
             role_arn: "arn:aws:iam::123456789012:role/EKSAdmin"


A Note on IAM User Permissions
------------------------------

The authenticating IAM user must have enough permissions on the EKS cluster to create and destroy pods and services. If you've set up your cluster with `hydro-project/eks-setup <https://github.com/hydro-project/eks-setup>`_, then any user you add using that script will have the appropriate privileges.

AWS Authentication Settings
---------------------------

.. automodule:: hydroplane.models.aws
  :members:
