Interacting with Hydroplane
===========================

To get Hydroplane running the first time, follow the :doc:`quickstart guide<quickstart>`.

.. contents::

The Hydroplane API
------------------

Hydroplane exposes a REST API over HTTP.

Hydroplane automatically generates detailed API documentation that it serves at

``http://<host and port of Hydroplane server>/docs``

You should refer to that documentation for the most up-to-date representation of the Hydroplane API.

This is a rough outline of the API's methods:

* ``POST /process`` - creates a process. The request body should be a JSON-serialized :doc:`process spec<processes>`
* ``GET /process`` - retrieves a list of all running processes
* ``GET /group/<group name>`` - retrieves a list of all processes in a particular group
* ``DELETE /process/<name of process>`` - destroys a process, given the process's name
* ``DELETE /group/<group name>`` - destroys all processes in a group


Command Line Tool (``hpctl``)
-----------------------------

The REST API is useful for programmatically interacting with Hydroplane, but it can be kind of a hassle to use directly. ``hpctl`` is a wrapper script that hides those calls behind a simple CLI.

To list the processes that are currently running:

.. code-block:: bash

    bin/hpctl list

To list only those processes in the group ``my-group``:

.. code-block:: bash

    bin/hpctl list -g my-group


To start a process using a :doc:`process spec<processes>` defined in ``foo.json``:

.. code-block:: bash

    bin/hpctl start foo.json

To stop a process named ``foo``:

.. code-block:: bash

    bin/hpctl stop foo

To stop all processes in the group ``my-group``

.. code-block:: bash

    bin/hpctl stop -g my-group


How does ``hpctl`` know which server to talk to?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``hpctl`` looks for the address of the Hydroplane server in the ``HYDROPLANE_SERVER`` environment variable. If that environment variable isn't defined, it falls back to Hydroplane's default host and port (``localhost:8000``). You can also specify the server's address explicitly with the ``-s/--server`` flag to ``hpctl``, e.g.:

.. code-block:: bash

   bin/hpctl -s hydroserver:4040 list
