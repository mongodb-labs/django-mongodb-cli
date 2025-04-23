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

    pip install -e .

.. _additional-installation-steps:

Additional installation steps
-----------------------------

.. note::

    ``just install`` also installs the ``dm`` command as shown above
    so in practice you can ``just install`` and skip the previous step.

Install ``dm`` command, clone and install third-party library
repositories and install dependencies with ``just install``.

::

    just install
