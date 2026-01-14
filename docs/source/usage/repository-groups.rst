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

Setting Up Remotes
-------------------

After cloning, you can setup git remotes for all repositories in a group::

    dm repo remote setup --group django

This will:

1. Add configured remotes (origin and upstream) for each repository
2. Fetch from all remotes

To list available groups::

    dm repo remote setup --list-groups

Setting Default Branches
-------------------------

To set the default branch for all repositories in a group::

    dm repo remote set-default --group django

Using with Just
---------------

The justfile has been simplified to use these dm group commands.
You can now run::

    just git-clone django
    just git-remote django

Which internally calls::

    dm repo clone --group django --install
    dm repo remote setup --group django
    dm repo remote set-default --group django

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
