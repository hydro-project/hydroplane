# hydroplane
A low-level service for launching processes on cloud infrastructure.

## Development

Hydroplane uses [poetry][poetry] to manage its dependencies. To get a development virtualenv set up:

```
pip install poetry
poetry shell
poetry install
```

### Managing Secrets Locally

Hydroplane needs some kind of secret store to store the credentials that it uses to communicate with workload management runtimes. We have a local secret store that stores secrets on the local filesystem, symmetrically-encrypted with a password. It's not meant for production use, but it should be enough for local development and experimentation.

Use the script `bin/local-secret-store` to manipulate the local secret store. For details on its usage, run `bin/local-secret-store --help`.

[poetry]: https://python-poetry.org/
