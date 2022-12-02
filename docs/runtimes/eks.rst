``eks`` - Amazon EKS
====================

The ``eks`` runtime integrates with EKS, AWS's managed Kubernetes offering.

.. contents::

Settings
--------

.. autopydantic_model:: hydroplane.runtimes.eks.Settings

Example Configuration
---------------------

Here's an example of a configuration file that uses the ``eks`` runtime and the ``local`` secret store. This configuration sets up Hydroplane to talk to an EKS cluster named ``my-cool-cluster`` in the ``us-west-2`` AWS region:

.. code-block:: yaml

    ---
    secret_store:
      secret_store_type: local
      store_location: ~/.hydro_secrets

    runtime:
      runtime_type: eks
      cluster_name: my-cool-cluster
      region: us-west-2
      credentials:
        access_key:
          access_key_id:
            secret_name: aws-credentials
            key: AccessKeyId
          secret_access_key:
            secret_name: aws-credentials
            key: SecretAccessKey


Quickstart
----------

Step 1: Create an EKS cluster and IAM user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to use the ``eks`` runtime, you first have to have an EKS cluster. We'll use `hydro-project/eks-setup <https://github.com/hydro-project/eks-setup>`_ to do that. Follow the instructions in the "Quickstart" section of that repo's README and then come back here.

When you're done with those instructions, you should have two things:

* An EKS cluster (we'll assume that the cluster's name is ``hydro-eks`` and that it was created in ``us-west-2`` in subsequent steps for brevity)
* The access key and secret key for a user in the cluster's ``cluster-admins`` group (if you added a user using ``eks-setup user add``, that user is in the ``cluster-admins`` group)


Step 2: Configure Hydroplane
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a file named ``eks.yml`` with the following contents:

.. code-block:: yaml

    ---
    secret_store:
      secret_store_type: local
      store_location: ~/.hydro_secrets

    runtime:
      runtime_type: eks
      cluster_name: hydro-eks
      region: us-west-2
      credentials:
        access_key:
          access_key_id:
            secret_name: aws-credentials
            key: AccessKeyId
          secret_access_key:
            secret_name: aws-credentials
            key: SecretAccessKey


If you haven't already, initialize your local secret store:

.. code-block:: bash

    bin/local-secret-store init


Make a note of the password you used when configuring the store; you'll need it when Hydroplane starts.

Now, create a file called ``creds.json`` that looks like this:

.. code-block:: json

    {"AccessKeyId":"<put your user's access key ID here>","SecretAccessKey":"<put your user's secret access key here>"}

Add that file to the secret store:

.. code-block:: bash

    bin/local-secret-store add -f creds.json aws-credentials


and delete the plaintext original afterwards:

.. code-block:: bash

    rm creds.json


Step 3: Run Hydroplane
^^^^^^^^^^^^^^^^^^^^^^

Now you've (finally) got an EKS cluster and the ability to authenticate to it! Let's launch Hydroplane:

.. code-block:: bash

    bin/hydroplane -c eks.yml

You'll be prompted for the password to your local secret store. Once you enter it, the server should bind and start accepting requests.

In a separate terminal, from the root of the ``hydroplane`` repo, let's make sure we can list processes:

.. code-block:: bash

   bin/hpctl list

You should get back an empty list, because we haven't launched any processes yet.

Let's try a simple example to make sure we can start something and access it remotely:

.. code-block:: bash

   bin/hpctl start examples/nginx.json

If you list processes with ``bin/hpctl list`` now, you should see something like this:

.. code-block:: json

    [
      {
        "process_name": "nginx",
        "group": null,
        "socket_addresses": [
          {
            "host": "34.217.208.197",
            "port": 31491,
            "is_public": true
          }
        ],
        "created": "2022-12-01T22:40:33+00:00"
      }
    ]

Note that the process is exposing a single public port. In this example, it's ``34.217.208.197:31491``, but your host and port will be different.

If you have ``jq`` installed, are on macOS, and want to open that server with a one-liner:

.. code-block:: bash

    open http://$(bin/hpctl list | jq -r "(.[0].socket_addresses[0].host + \":\" + (.[0].socket_addresses[0].port|tostring))")

Otherwise, you can copy-paste the host and port into a browser window. Either way, you should see an `nginx <https://www.nginx.com/>`_ "hello world" page.

Now that we've verified that everything is working, let's stop the process:

.. code-block:: bash

    bin/hpctl stop nginx


Implementation and Configuration Details
----------------------------------------

How the ``eks`` Runtime Creates Processes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each process is run in EKS as a single pod and an associated service. The service is there to give Kubernetes something to expose to the Internet when a process has a public IP address, and to give processes an easy way to name one another without relying on any kind of third-party service discovery mechanism. Private services only need to be routable and discoverable within the cluster, so their associated services are ``ClusterIP`` services. Public services need to be routable from outside the cluster, so we have to handle them separately.

In a typical Kubernetes service where you have one service backing an auto-scaling collection of pods, you'd put a ``LoadBalancer`` service in front of the pods that round-robins traffic between them. In our case, we're expecting something higher-level than us to do things like load balancing, so we want each process to be named and exposed individually. If we were to create a ``LoadBalancer`` service per process, we'd also be creating a separate **load balancer** per process, and load balancers in AWS are really expensive. Instead, we create a ``NodePort`` service for each process that routes only to that process's pod. A ``NodePort`` service exposes a high-numbered port on every node in the cluster, and all traffic to that port on any cluster node is transparently routed to the pod by Kubernetes' overlay network.

Using ``NodePort`` services does what we want without paying for additional resources, but it also makes it look from the client's perspective like the process is running on every node in the cluster at once, which is inconsistent from the abstraction presented by other runtimes. To maintain the illusion that the process is only accessible from one node, we do some introspection to determine the cluster node that the pod is actually running on and only list that node's IP address when providing information about the process in response to list calls.


Authenticating with AWS
^^^^^^^^^^^^^^^^^^^^^^^

In order for Hydroplane to launch processes on an EKS cluster, it must be able to authenticate with that cluster. To authenticate, you'll need an AWS `access key ID and corresponding secret access key <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html>`_. These credentials will need to be stored in Hydroplane's :doc:`secret store </secrets>`.

.. _eks-secret-example:

Authenticating with IAM Credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

AWS Authentication Configuration Reference
------------------------------------------

.. automodule:: hydroplane.models.aws
  :members:
