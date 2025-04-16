Installation
============

Clone the repository
--------------------

::

    git clone https://github.com/mongodb-labs/django-mongodb-cli
    cd django-mongodb-cli


Create a virtual environment
----------------------------

::

    python -m venv .venv
    source .venv/bin/activate


Install CLI
-----------

::

    python -m pip install -e .

Install development dependencies
--------------------------------

::

    dm repo clone -a

Usage
-----

.. code:: bash

    $ dm --help
    Usage: dm [OPTIONS] COMMAND [ARGS]...

      Django MongoDB CLI

    Options:
      --help  Show this message and exit.

    Commands:
      repo          Run Django fork and third-party library tests.
      startproject  Run `startproject` with custom templates.
