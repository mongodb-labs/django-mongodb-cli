Repository Groups
=================

The ``dm`` CLI supports organizing repositories into groups for easier management.
This allows you to clone and configure multiple related repositories with a single command.

Available Groups
----------------

To see all available repository groups::

    dm repo clone --list-groups

Example output::

    Available repository groups:
      django: django, django-mongodb-backend, django-mongodb-extensions, libmongocrypt, mongo-python-driver
      langchain: langchain-mongodb, pymongo-search-utils
      mongo-arrow: mongo-arrow

Cloning Repository Groups
--------------------------

To clone all repositories in a group::

    dm repo clone --group django

To clone and install packages::

    dm repo clone --group django --install

Showing and Setting Up Remotes
-------------------------------

To show git remotes for a single repository::

    dm repo remote django

This will automatically setup remotes if the repository belongs to a group and remotes are configured for it.

To show git remotes for all repositories in a group::

    dm repo remote --group django

Both commands will:

1. Automatically setup remotes if not already configured (based on pyproject.toml configuration)
2. Display all configured remotes for each repository

The commands are idempotent - running them multiple times will not re-add existing remotes.

To list available groups::

    dm repo remote --list-groups

Setting Default Branches
-------------------------

To set the default branch for all repositories in a group::

    dm repo set-default --group django

Opening Repositories in Browser
--------------------------------

To open all repositories in a group in your default web browser::

    dm repo open --group django

This will open the GitHub page for each repository in the group using the ``gh browse`` command.

Using with Just
---------------

The justfile has been simplified to use these dm group commands.
You can now run::

    just git-clone django
    just git-remote django

Which internally calls::

    dm repo clone --group django --install
    dm repo remote --group django
    dm repo set-default --group django

Configuring Groups
------------------

Repository groups are configured in ``pyproject.toml`` under::

    [tool.django-mongodb-cli.groups]
    django = [
        "django",
        "django-mongodb-backend",
        "django-mongodb-extensions",
        "libmongocrypt",
        "mongo-python-driver",
    ]

Remote configurations are defined under::

    [tool.django-mongodb-cli.remotes.django.django-mongodb-backend]
    origin = "git+ssh://git@github.com/aclark4life/django-mongodb-backend"
    upstream = "git+ssh://git@github.com/mongodb/django-mongodb-backend"

Benefits
--------

* **Simplified workflow**: Clone and configure multiple related repositories with one command
* **Consistent setup**: Ensures all team members have the same remote configurations
* **Less error-prone**: Reduces manual commands and potential mistakes
* **Better organization**: Logically groups related repositories together
