Quickstart Guide
================

This quickstart guide will get you from zero to a running Hydroplane server as quickly as possible. This guide has been tested on macOS 12 (Monterey), but should work with minimal modification on recent versions of macOS and Linux.

.. code-block:: bash

    # Download and install Docker Desktop
    open "https://www.docker.com/products/docker-desktop/"
    
    # Launch the Docker Desktop app on your machine

    # Clone the hydroplane repo and enter it
    git clone git@github.com:hydro-project/hydroplane.git
    cd hydroplane

    # Make sure you're running Python 3.10 or later
    python3 --version

    # Install poetry if you haven't already
    # (see https://python-poetry.org/docs/ for more info)
    curl -sSL https://install.python-poetry.org | python3 -

    # Use poetry to initialize Hydroplane's virtualenv and install its dependencies
    poetry shell
    poetry install

    # Start the Hydroplane server
    # (uses the checked-in `basic-config.yml` config file by default)
    bin/hydroplane

    # In a separate terminal, from the root of the hydroplane repo, list processes.
    # This should print '[]', since no processes are running at first.
    bin/hpctl list

    # Let's start a simple example process
    bin/hpctl start examples/nginx.json

    # Load localhost:8080 in a browser; you should see an nginx "hello world" page
    open "http://localhost:8080/"
