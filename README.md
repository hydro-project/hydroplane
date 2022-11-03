# hydroplane
A service for launching containerized processes on cloud infrastructure.

## Concepts

Hydroplane is meant to act as a simple, unified API for starting and stopping processes (deployed as Docker containers) on multiple different _backend runtimes_ in a way that abstracts as much of the complexity from connecting to and interacting with those runtimes as possible.

Hydroplane currently supports the following runtimes:

* Docker (single-node)
* Amazon EKS

## Getting Started

### Setting Up Your Development Environment

Hydroplane uses [poetry][poetry] to manage its dependencies. To get a development virtualenv set up:

```
pip install poetry
poetry shell
poetry install
```

### Initializing a Local Secret Store

Hydroplane needs some form of secret store to safely keep credentials that it uses to communicate with the backend runtime. We have a local secret store that stores secrets on the local filesystem, symetrically encrypted with a password. It's not meant for production use, but it should be good enough for local development and experimentation.

To initialize your local secret store:

```
poetry run bin/local-secret-store init
```

You'll be prompted to enter a password for the secret store. By default, it will be initialized in `~/.hydro_secrets` but you can change its location by adding the `--store-location` flag to the above command.

### Configuring Hydroplane

To run Hydroplane, you must configure how it accesses both the secret store and the backend runtime. Here's a simple example that uses the single-node Docker runtime and the local secret store.

```yaml
---
secret_store:
  secret_store_type: local
  store_location: ~/.hydro_secrets

runtime:
  runtime_type: docker
```


### Managing Secrets Locally

Hydroplane needs some kind of secret store to store the credentials that it uses to communicate with workload management runtimes. We have a local secret store that stores secrets on the local filesystem, symmetrically-encrypted with a password. It's not meant for production use, but it should be enough for local development and experimentation.

Use the script `bin/local-secret-store` to manipulate the local secret store. For details on its usage, run `bin/local-secret-store --help`.

[poetry]: https://python-poetry.org/
