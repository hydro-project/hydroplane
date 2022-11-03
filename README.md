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

[poetry]: https://python-poetry.org/
