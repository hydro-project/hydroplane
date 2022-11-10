The Hydroplane API
------------------

Hydroplane automatically generates detailed API documentation that it serves at

``http://<host and port of Hydroplane server>/docs``

You should refer to that documentation for the most up-to-date representation of the Hydroplane API.

This is a rough outline of the API's methods:

* ``POST /process`` - creates a process. The request body should be a JSON-serialized :doc:`process spec<processes>`
* ``GET /process`` - retrieves a list of all running processes
* ``GET /group/<group name>`` - retrieves a list of all processes in a particular group
* ``DELETE /process/<name of process>`` - destroys a process, given the process's name
* ``DELETE /group/<group name>`` - destroys all processes in a group
