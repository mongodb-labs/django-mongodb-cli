Installation Configuration
===========================

The ``dm`` CLI supports customizing how packages are installed from cloned repositories
through configuration in ``pyproject.toml``.

Basic Configuration
-------------------

You can configure installation settings for each repository under::

    [tool.django-mongodb-cli.install.<repo-name>]

Custom Install Directory
------------------------

If a package needs to be installed from a subdirectory (common with monorepos)::

    [tool.django-mongodb-cli.install.mongo-arrow]
    install_dirs = ["bindings/python"]

This will install from ``src/mongo-arrow/bindings/python`` instead of ``src/mongo-arrow``.

Multiple Install Directories
-----------------------------

For monorepos with multiple packages, you can specify multiple directories to install::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dirs = ["libs/langchain-mongodb", "libs/langgraph-store-mongodb"]

This will run ``uv pip install -e`` for each directory:

1. ``uv pip install -e src/langchain-mongodb/libs/langchain-mongodb``
2. ``uv pip install -e src/langchain-mongodb/libs/langgraph-store-mongodb``

**Note**: For backward compatibility, ``install_dir`` (singular) is still supported for single directories.

Environment Variables
---------------------

You can set environment variables for the installation process::

    [tool.django-mongodb-cli.install.mongo-arrow]
    install_dirs = ["bindings/python"]

    [[tool.django-mongodb-cli.install.mongo-arrow.env_vars]]
    name = "LDFLAGS"
    value = "-L/opt/homebrew/opt/mongo-c-driver@1/lib"

    [[tool.django-mongodb-cli.install.mongo-arrow.env_vars]]
    name = "CPPFLAGS"
    value = "-I/opt/homebrew/opt/mongo-c-driver@1/include"

Optional Extras
---------------

You can install optional extras (also known as optional dependencies) defined in the
package's ``[project.optional-dependencies]`` section::

    [tool.django-mongodb-cli.install.some-package]
    extras = ["security", "performance"]

This will run:

1. ``uv pip install -e src/some-package`` (base package)
2. ``uv pip install -e src/some-package[security]`` (security extra)
3. ``uv pip install -e src/some-package[performance]`` (performance extra)

The ``extras`` option is useful when:

* The package has optional features that require additional dependencies
* You need specific functionality that's not included in the base installation
* You want to install testing or development extras

Dependency Groups (PEP 735)
----------------------------

You can install dependency groups defined in the package's ``pyproject.toml`` using
the PEP 735 standard::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dirs = ["libs/langchain-mongodb"]
    groups = ["dev", "test"]

This will run:

1. ``uv pip install -e src/langchain-mongodb/libs/langchain-mongodb`` (base package)
2. ``pip install --group src/langchain-mongodb/libs/langchain-mongodb/pyproject.toml:dev`` (dev group)
3. ``pip install --group src/langchain-mongodb/libs/langchain-mongodb/pyproject.toml:test`` (test group)

The ``groups`` option uses ``pip install --group`` (available in pip 25.3+) to install
dependency groups defined in ``[dependency-groups]`` section of the package's ``pyproject.toml``
according to PEP 735.

The ``groups`` option is useful when:

* You need development dependencies from the package
* You want to run tests that require test dependencies
* The package defines multiple dependency groups for different use cases

Combining Extras and Groups
----------------------------

You can use both ``extras`` and ``groups`` together::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dirs = ["libs/langchain-mongodb"]
    extras = ["community"]
    groups = ["dev", "test"]

This will install:

1. Base package from each directory
2. All specified extras for each directory (using ``pip install -e path[extra]``)
3. All specified dependency groups for each directory (using ``pip install --group``)

Example: langchain-mongodb
---------------------------

Here's a complete example for configuring ``langchain-mongodb``::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dirs = ["libs/langchain-mongodb"]
    extras = ["community"]
    groups = ["dev", "test", "lint"]

This configuration assumes ``langchain-mongodb`` has a ``pyproject.toml`` with::

    [project.optional-dependencies]
    community = ["langchain-community>=0.3.0"]

    [dependency-groups]
    dev = ["pytest", "ruff", "mypy"]
    test = ["pytest-cov", "pytest-asyncio"]
    lint = ["ruff", "mypy"]

When you run::

    dm repo install langchain-mongodb

The CLI will:

1. Install the base package from ``src/langchain-mongodb/libs/langchain-mongodb``
2. Install the ``community`` extra using ``uv pip install -e path[community]``
3. Install the ``dev`` dependency group using ``pip install --group``
4. Install the ``test`` dependency group using ``pip install --group``
5. Install the ``lint`` dependency group using ``pip install --group``

Note: Dependency groups require pip 25.3 or later, which supports PEP 735.

Benefits
--------

* **Automated setup**: Install all required dependencies in one command
* **Reproducible environments**: Ensure all team members have the same dependencies
* **Developer convenience**: No need to manually install optional groups
* **CI/CD integration**: Use the same command in automated pipelines
