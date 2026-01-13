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
    install_dir = "bindings/python"

This will install from ``src/mongo-arrow/bindings/python`` instead of ``src/mongo-arrow``.

Environment Variables
---------------------

You can set environment variables for the installation process::

    [tool.django-mongodb-cli.install.mongo-arrow]
    install_dir = "bindings/python"
    
    [[tool.django-mongodb-cli.install.mongo-arrow.env_vars]]
    name = "LDFLAGS"
    value = "-L/opt/homebrew/opt/mongo-c-driver@1/lib"
    
    [[tool.django-mongodb-cli.install.mongo-arrow.env_vars]]
    name = "CPPFLAGS"
    value = "-I/opt/homebrew/opt/mongo-c-driver@1/include"

Optional Dependency Groups
--------------------------

You can install optional dependency groups defined in the package's ``pyproject.toml``::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dir = "libs/langchain-mongodb"
    groups = ["dev", "test"]

This will run:

1. ``uv pip install -e src/langchain-mongodb/libs/langchain-mongodb`` (base package)
2. ``uv pip install -e src/langchain-mongodb/libs/langchain-mongodb[dev]`` (dev group)
3. ``uv pip install -e src/langchain-mongodb/libs/langchain-mongodb[test]`` (test group)

The ``groups`` option is useful when:

* You need development dependencies from the package
* You want to run tests that require test dependencies
* The package defines multiple optional feature sets

Example: langchain-mongodb
---------------------------

Here's a complete example for configuring ``langchain-mongodb``::

    [tool.django-mongodb-cli.install.langchain-mongodb]
    install_dir = "libs/langchain-mongodb"
    groups = ["dev", "test", "community"]

This configuration assumes ``langchain-mongodb`` has a ``pyproject.toml`` with::

    [project.optional-dependencies]
    dev = ["pytest", "ruff", "mypy"]
    test = ["pytest-cov", "pytest-asyncio"]
    community = ["langchain-community"]

When you run::

    dm repo install langchain-mongodb

The CLI will:

1. Install the base package from ``src/langchain-mongodb/libs/langchain-mongodb``
2. Install the ``dev`` group with its dependencies
3. Install the ``test`` group with its dependencies
4. Install the ``community`` group with its dependencies

Benefits
--------

* **Automated setup**: Install all required dependencies in one command
* **Reproducible environments**: Ensure all team members have the same dependencies
* **Developer convenience**: No need to manually install optional groups
* **CI/CD integration**: Use the same command in automated pipelines
