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


Install ``dm`` command
----------------------

::

    python -m pip install -e .

.. _additional-installation-steps:

Additional installation steps
-----------------------------

Clone third-party library repositories and install dependencies with ``just``.

::

    just install
