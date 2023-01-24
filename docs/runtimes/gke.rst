``gke`` - Google Kubernetes Engine
==================================

The ``gke`` runtime integrates with GKE, GCP's managed Kubernetes offering.

.. contents::

Settings
--------

.. autopydantic_model:: hydroplane.runtimes.gke.Settings

Example Configuration
---------------------

Here's an example of a configuration file that uses the ``gke`` runtime. This runtime doesn't need access to a secret store, so we're using the ``none`` secret store here.

.. code-block:: yaml

    ---
    secret_store:
        secret_store_type: none

    runtime:
        runtime_type: gke
        cluster_id: hydroplane-test-cluster
        project: hydro-development
        region: us-central1

Quickstart
----------

We'll assume that we're creating a cluster named ``hydroplane-test-cluster`` in the ``us-central1`` region, running within a VPC named ``hydroplane-vpc``, inside a project named ``test-project``. Substitute your cluster, VPC and project name(s) as appropriate.

Step 0: Set Up Your Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you have the Google Cloud command-line tool (``gcloud``) installed. You can install it by following the instructions `here <https://cloud.google.com/sdk/docs/install>`_.

Once you've got ``gcloud`` installed, you'll need to authenticate:

.. code-block:: bash

    # First, we'll login as you.
    gcloud auth login

    # Next, we'll make sure you've got a project configured, so that you
    # don't have to specify which project you're referring to every time
    # you run a command.
    gcloud config set project test-project

    # Finally, we'll configure some local Application Default Credentials
    # that Hydroplane can use to act on your behalf.
    gcloud auth application-default login


Step 1: Create a VPC If Needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Your GKE cluster will need a VPC to run within. If you don't already have a VPC configured in your GCP project, you can create a VPC by following `these instructions <https://cloud.google.com/vpc/docs/create-modify-vpc-networks#create-auto-network>`_, or run the following:

.. code-block:: bash

    gcloud compute networks create \
        hydroplane-vpc \
        --subnet-mode=auto \
        --mtu=1460 \
        --bgp-routing-mode=regional

We'll assume that the VPC is named ``hydroplane-vpc``, and was configured in auto mode (so all its subnets are also called ``hydroplane-vpc``).

By default, VPC networks aren't routable from outside GCP. If you want to connect to your public processes from outside GCP, you'll need to poke a hole in the VPC's firewall.

To start, we'll poke a hole in the firewall for our IP address. To do that, run:

.. code-block:: bash

    gcloud compute firewall-rules create \
        allow-my-ip \
        --direction=INGRESS \
        --priority=999 \
        --network=hydroplane-vpc \
        --action=ALLOW \
        --rules=all \
        --source-ranges=$(curl -s https://api.ipify.org)/32

If you want to add more source ranges, you can add more firewall rules similar to the one declared above, setting ``--source-ranges`` to whatever ranges you want to open.

Step 2: Create a GKE Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

GCP provides a service called `Autopilot mode <https://cloud.google.com/kubernetes-engine/docs/concepts/types-of-clusters#modes>`_ that manages most of the minutiae of setting up a Kubernetes cluster for you. Follow the instructions in `this document <https://cloud.google.com/kubernetes-engine/docs/how-to/creating-an-autopilot-cluster>`_ to create a cluster in Autopilot mode, or just run the following, filling in the blanks as appropriate:

.. code-block:: bash

    gcloud container clusters create-auto \
        "hydroplane-test-cluster" \
        --region "us-central1" \
        --release-channel "regular" \
        --network "projects/test-project/global/networks/hydroplane-vpc" \
        --subnetwork "projects/test-project/regions/us-central1/subnetworks/hydroplane-vpc" \
        --cluster-ipv4-cidr "/17" \
        --services-ipv4-cidr "/22"

Step 3: Configure Hydroplane
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a file named ``gke.yml`` with the following contents (filling in the blanks):

.. code-block:: yaml

    ---
    secret_store:
        secret_store_type: none

    runtime:
        runtime_type: gke
        cluster_id: hydroplane-test-cluster
        project: test-project
        region: us-central1

Step 4: Run Hydroplane
^^^^^^^^^^^^^^^^^^^^^^

You should now have everything you need. Let's launch Hydroplane:

.. code-block:: bash

    bin/hydroplane -c gke.yml

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
        "created": "2022-12-01T22:40:33+00:00",
        "status": "RUNNING"
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

For details on how the ``gke`` runtime creates processes, see :doc:`/architecture/k8s`.

Authenticating with GCP
^^^^^^^^^^^^^^^^^^^^^^^

Hydroplane uses Application Default Credentials (ADC) to connect to GCP. ADC is a strategy that Google's authentication libraries use to locate credentials and make them available to the various client libraries for GCP services. More information about ADC can be found `in the GCP docs <https://cloud.google.com/docs/authentication/application-default-credentials>`_.

Once you've populated ADC on your machine by running ``gcloud auth application-default login``, Hydroplane should be able to pick up your credentials automatically. The ``gke`` runtime will also periodically refresh its credentials, so you shouldn't need to log in again after you've logged in the first time.