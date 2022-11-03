Secrets
=======

Both Hydroplane and the processes it creates need access to secret values. Some secret values (**Hydroplane secrets**) are used by Hydroplane to authenticate with the runtime. Other secret values (**process secrets**) are used by processes when they run.

Hydroplane Secrets
------------------

Hydroplane secrets are stored in a **secret store**. Hydroplane needs access to this secret store in order to retrieve enough credentials to authenticate with the runtime.

.. autopydantic_model:: hydroplane.models.secret.HydroplaneSecret

.. toctree::
   :maxdepth: 1
   :caption: Available Secret Stores

   secret_stores/local

Process Secrets
---------------

Process secrets are either stored by the runtime itself, or by a companion secret storage system.

.. autopydantic_model:: hydroplane.models.secret.ProcessSecret
