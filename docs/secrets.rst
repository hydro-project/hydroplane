Secrets
=======

Secret Values
-------------

Some parts of a `process's<processes>` process spec or a `runtime<runtimes>`'s settings are things like API tokens and passwords that you don't want to pass around and store in cleartext. Hydroplane uses ``SecretValue`` to refer to these values:

.. autopydantic_model:: hydroplane.models.secret.SecretValue

Some secret values are used by Hydroplane to authenticate with the runtime; we'll call those **Hydroplane secrets**. Other secret values are used by processes when they run; we'll call those **process secrets**. Hydroplane uses ``SecretValue`` to refer to both kinds of secrets, but handles them a bit differently.

Hydroplane Secrets
~~~~~~~~~~~~~~~~~~

Hydroplane secrets are stored in a **secret store**. Hydroplane needs access to this secret store in order to retrieve enough credentials to authenticate with the runtime.

.. toctree::
   :maxdepth: 1
   :caption: Available Secret Stores

   secret_stores/local


Process Secrets
---------------
