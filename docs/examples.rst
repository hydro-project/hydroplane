Example Process Specs
=====================

.. contents::

Web Server
----------

The file `examples/nginx.json <https://github.com/hydro-project/hydroplane/blob/main/examples/nginx.json>`_ is the process spec for a simple "hello world" `nginx <https://www.nginx.com/>`_ webserver.

Launching the Process
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # From the root of the repo
    bin/hpctl start examples/nginx.json


Making Sure It Worked
^^^^^^^^^^^^^^^^^^^^^

$s in the code block below denote commands; the rest is example output.

.. code-block:: bash

    $ bin/hpctl list

    [
      {
        "process_name": "nginx",
        "group": null,
        "socket_addresses": [
          {
            "host": "0.0.0.0",
            "port": 8080,
            "is_public": true
          }
        ],
        "created": "2022-12-01T20:25:36.009608+00:00"
      }
    ]

    # Note the host and port and concat them together
    $ open http://0.0.0.0:8080

or, if you've got `jq` on macOS and want a one-liner:

.. code-block:: bash

    open http://$(bin/hpctl list | jq -r "(.[0].socket_addresses[0].host + \":\" + (.[0].socket_addresses[0].port|tostring))")


Stopping the Process
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bin/hpctl stop nginx

Chat
----

The JSON files in `examples/chat <https://github.com/hydro-project/hydroplane/tree/main/examples/chat>`_ are the process specs for three processes: a chat server and two chat clients. Details of how the client and server work can be found in the `hydroflow repo <https://github.com/hydro-project/hydroflow/tree/main/hydroflow/examples/chat>`_.

Launching the Processes
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Launch the server (from the root of this repo)
    bin/hpctl start examples/chat/chat-server.json

    # Give the server some time to warm up
    sleep 5

    # Start the clients
    bin/hpctl start examples/chat/chat-client-alice.json
    bin/hpctl start examples/chat/chat-client-bob.json


Making Sure It Worked
^^^^^^^^^^^^^^^^^^^^^

The chat server and clients don't have any public interfaces, so we'll to look at their logs to make sure they're working.

In the ``docker`` runtime:

.. code-block:: bash

    # Check that processes exist; should see a server container and two client containers
    docker ps

    # Check the server's logs. It should report that it's ready.
    docker logs chat-server

    # Check the clients' logs. You should see both alice and bob sending random messages to each other.
    docker logs chat-client-alice
    docker logs chat-client-bob

In the ``eks`` runtime:

.. code-block:: bash

    # Check that pods for each process exist; should see three of them, one per process
    kubectl get pods

    # Check the server's logs. It should report that it's ready.
    kubectl logs pod/chat-server

    # Check the clients' logs. You should see both alice and bob sending random messages to each other.
    kubectl logs pod/chat-client-alice
    kubectl logs pod/chat-client-bob


Stopping the Processes
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    bin/hpctl stop -g chat-clients
    bin/hpctl stop chat-server
