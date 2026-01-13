# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Tooling and setup

- This project is a Python package that installs a CLI named `dm` (Django MongoDB CLI).
- The CLI is intended to be used from the repository root, where `pyproject.toml` defines the `[tool.django-mongodb-cli]` configuration.

### Environment and installation

From a clean clone:

```bash path=null start=null
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The docs also define a convenience target using `just` (preferred for local setup):

```bash path=null start=null
just install
```

`just install` will:
- Ensure a virtualenv is active (`check-venv` recipe).
- Install system packages and Python dependencies (including editable install of this package).
- Install `pre-commit` hooks.

## Common commands

All commands below assume you are in the repo root with the virtualenv activated.

### Working with the `dm` CLI

The entry point for this project is the `dm` command, exposed by the `project.scripts` section of `pyproject.toml` and implemented in `django_mongodb_cli.__init__.py`.

High-level subcommands:
- `dm app ...` — manage Django apps inside a project (`django_mongodb_cli/app.py`).
- `dm frontend ...` — manage a Django "frontend" app and its Node/npm tooling (`django_mongodb_cli/frontend.py`).
- `dm project ...` — scaffold and manage Django projects (`django_mongodb_cli/project.py`).
- `dm repo ...` — manage and test external Git repos configured in `[tool.django-mongodb-cli]` (`django_mongodb_cli/repo.py`, `django_mongodb_cli/utils.py`).

#### Project lifecycle

Project scaffolding and management all assume you are in a workspace where you want to create/run a Django project; commands operate relative to the current directory.

- Create a new project from the bundled template:

  ```bash path=null start=null
  dm project add <project_name> [--add-frontend]
  ```

  This uses the `project_template` under `django_mongodb_cli/templates` via `django-admin startproject`. It also generates a per-project `pyproject.toml` preconfigured for MongoDB usage and testing.

- Run a project (using `django-admin` instead of `manage.py`):

  ```bash path=null start=null
  dm project run <project_name> [--frontend] [--mongodb-uri MONGODB_URI]
  ```

  - Uses `DJANGO_SETTINGS_MODULE=<project_name>.<settings_path>` where `settings_path` comes from `[tool.django-mongodb-cli.project.settings.path]` in the root `pyproject.toml` (defaults to a `settings.base`-style module if not overridden).
  - If `--frontend` is passed, it will ensure the frontend is installed (`dm frontend install ...`) and run the chosen npm script alongside the Django server.
  - `--mongodb-uri` (or the `MONGODB_URI` environment variable) is passed through to Django via `_build_mongodb_env`.

- Migrations at the project level:

  ```bash path=null start=null
  dm project makemigrations <project_name> [app_label] [--mongodb-uri ...]
  dm project migrate <project_name> [app_label] [migration_name] [--database NAME] [--mongodb-uri ...]
  ```

- Run arbitrary `django-admin` commands for a project:

  ```bash path=null start=null
  dm project manage <project_name> [command] [args...] [--mongodb-uri ...] [--database NAME]
  ```

  If `command` is omitted, `django-admin` is invoked with no arguments for the configured project.

- Non-interactive superuser creation:

  ```bash path=null start=null
  dm project su <project_name> [--username USER] [--password PASS] [--email EMAIL] [--mongodb-uri ...]
  ```

  This uses `DJANGO_SUPERUSER_PASSWORD` and `MONGODB_URI` environment variables under the hood.

#### App-level commands

App commands assume an existing Django project directory under the specified `project_name`.

- Create/remove a Django app using the packaged template:

  ```bash path=null start=null
  dm app create <app_name> <project_name> [--directory PATH]
  dm app remove <app_name> <project_name> [--directory PATH]
  ```

- App-specific migrations (wrappers around `django-admin` with `DJANGO_SETTINGS_MODULE` set to `<project_name>.settings`):

  ```bash path=null start=null
  dm app makemigrations <project_name> <app_label> [--directory PATH]
  dm app migrate <project_name> [app_label] [migration_name] [--directory PATH]
  ```

#### Frontend helpers

Frontend helpers assume a `frontend` app inside the Django project (or another directory if overridden).

- Scaffold the frontend app from the bundled template:

  ```bash path=null start=null
  dm frontend create <project_name> [--directory PATH]
  ```

- Remove the frontend app:

  ```bash path=null start=null
  dm frontend remove <project_name> [--directory PATH]
  ```

- Install npm dependencies in the frontend directory:

  ```bash path=null start=null
  dm frontend install <project_name> [--frontend-dir frontend] [--directory PATH] [--clean]
  ```

- Run an npm script in the frontend directory (defaults to `watch`):

  ```bash path=null start=null
  dm frontend run <project_name> [--frontend-dir frontend] [--directory PATH] [--script SCRIPT]
  ```

### Managing external repos (`dm repo`)

External repositories and their Git URLs are defined under `[tool.django-mongodb-cli.repos]` in the root `pyproject.toml`. By default they are cloned under `path = "src"` from that same config.

Key patterns:

- List known repos from config and filesystem:

  ```bash path=null start=null
  dm repo --list-repos
  ```

- Clone one or more configured repos (optionally installing their Python packages):

  ```bash path=null start=null
  dm repo clone <repo_name> [--install]
  dm repo clone --all-repos [--install]
  ```

  Clone behavior (paths, branches, etc.) is driven by `Repo.get_map()` and `Repo.parse_git_url()` in `django_mongodb_cli/utils.py`.

- Set up Git remotes and defaults via `dm repo remote` and `dm repo set-default` (these are wrapped in convenient `just git-remote` recipes for common groups like `django`, `langchain`, `mongo-arrow`).

- Inspect and maintain repos:

  ```bash path=null start=null
  dm repo status <repo_name> [--all-repos]
  dm repo diff <repo_name> [--all-repos]
  dm repo fetch <repo_name> [--all-repos]
  dm repo pull <repo_name> [--all-repos]
  dm repo push <repo_name> [--all-repos]
  dm repo log <repo_name> [--all-repos]
  dm repo open <repo_name> [--all-repos]
  dm repo reset <repo_name> [--all-repos]
  ```

- Manage branches for a repo or across repos:

  ```bash path=null start=null
  dm repo checkout <repo_name> [branch_name] [--list-branches] [--all-repos] [--delete-branch] [--cloned-only]
  ```

- Create Evergreen patches using project configuration in `[tool.django-mongodb-cli.evergreen.<repo_name>]`:

  ```bash path=null start=null
  dm repo patch <repo_name>
  ```

- Create GitHub PRs for a repo using `gh pr create`:

  ```bash path=null start=null
  dm repo pr <repo_name> [--all-repos]
  ```

### Running tests

Tests are generally run *in external repositories* managed by this CLI; there are no standalone tests for the CLI package itself.

#### Running test suites for a configured repo

Testing behavior is driven by the `[tool.django-mongodb-cli.test.<repo_name>]` blocks in `pyproject.toml`. `django_mongodb_cli.utils.Test` reads this configuration to decide:
- Which command to run (`pytest`, `./runtests.py`, or `just`).
- Which directories to run tests from (`test_dirs`).
- Any additional options (`test_options`, `env_vars`, `settings.module`, etc.).

The high-level command is:

```bash path=null start=null
dm repo test <repo_name> [modules...] [--keepdb] [--keyword PATTERN] [--list-tests] [--setenv] [--mongodb-uri URI]
```

Notes:
- If `--mongodb-uri` is provided (or `MONGODB_URI` is already set), it is exported to the environment before running tests.
- If `--list-tests` is passed, the tool recursively walks the configured `test_dirs` and prints discovered Python test files instead of executing them.
- If one or more `modules` are given, they are appended to the underlying test command, allowing you to scope test runs to a specific test module or package.

Example patterns (adapt to a specific repo and path):

- Run the default test suite for Django itself:

  ```bash path=null start=null
  dm repo test django
  ```

- Run tests for `django-rest-framework` with verbose pytest output (driven by its `test` config in `pyproject.toml`):

  ```bash path=null start=null
  dm repo test django-rest-framework
  ```

- Run a single test module (path is relative to the configured `test_dirs` for that repo):

  ```bash path=null start=null
  dm repo test <repo_name> path/to/test_module.py
  ```

- Run tests whose names match a keyword:

  ```bash path=null start=null
  dm repo test <repo_name> --keyword "mongo"
  ```

### Docs (Sphinx)

The `docs/` tree contains Sphinx documentation for this project (`docs/source/index.rst` is the root). There is both a Sphinx `Makefile` and `just` recipes for common operations.

- Build HTML docs via Sphinx `Makefile`:

  ```bash path=null start=null
  make -C docs html
  ```

- Or use `just` helpers:

  ```bash path=null start=null
  just sphinx-build        # build HTML into docs/_build
  just sphinx-autobuild    # rebuild docs on changes
  just sphinx-open         # open docs/_build/index.html
  just sphinx-clean        # remove docs/_build
  ```

Make sure any Sphinx-specific Python requirements are installed; `docs/requirements.txt` currently lists the extra packages used.

## Architecture overview

### Purpose and scope

The primary purpose of this repository is to provide the `dm` CLI, which helps maintain and test a ecosystem of repositories around `django-mongodb-backend`, third-party Django libraries, and MongoDB-focused integrations. Most of the heavy lifting (tests, app code, etc.) happens in those external repos; this project coordinates their cloning, configuration, and test execution, and it can also scaffold new Django projects and apps that are pre-wired for MongoDB.

### CLI entrypoint and subcommand layout

- `django_mongodb_cli/__init__.py` defines the top-level Typer app (`dm`) and attaches four sub-Typer instances: `app`, `frontend`, `project`, and `repo`.
- The CLI uses Typer’s callback mechanism to show help when no subcommand is invoked.
- The executable entrypoint is wired in `pyproject.toml` under `[project.scripts]` as `dm = "django_mongodb_cli:dm"`.

### Configuration via `pyproject.toml`

`django_mongodb_cli.utils.Repo` loads the root `pyproject.toml` and extracts the `[tool.django-mongodb-cli]` section into `self._tool_cfg`. This configuration drives almost all higher-level behavior:

- `path` — base directory where external Git repos are cloned (currently `src`).
- `repos` — list of `"name @ git+ssh://..."` strings parsed into a mapping of logical repo names to Git URLs.
- `install.<repo_name>` — per-repo installation metadata (e.g., `install_dir`, extra `env_vars`). Used by `Package.install_package` when called via `dm repo install` or `dm repo clone --install`.
- `test.<repo_name>` — per-repo test configuration, used by `Test.run_tests` and `dm repo test` to:
  - Determine `test_dirs` for the test directories.
  - Specify `test_command` (`pytest`, `./runtests.py`, or `just`).
  - Provide additional `test_options`, settings modules, and environment variables.
  - Configure templates for MongoDB-specific settings files, migrations, and app configs that are copied into external repos prior to running tests.
- `origin.<repo_name>` and `evergreen.<repo_name>` — control how `Repo.get_repo_origin` rewrites origin URLs and how Evergreen patches are created for selected repos.
- `project.settings.path` — default settings module path used by `dm project` when constructing `DJANGO_SETTINGS_MODULE` (e.g., `settings.qe`).

Because `Repo`, `Package`, and `Test` all read from this shared configuration, changes to `pyproject.toml` propagate through the tooling without needing to modify CLI code.

### Repository orchestration (`Repo`, `Package`, `Test`)

- `django_mongodb_cli/utils.py` defines three core classes:
  - `Repo` — generic Git/repo operations (clone, status, diff, log, checkout, fetch, pull, push, reset, open, etc.), plus helpers for listing and mapping repos from config.
  - `Package(Repo)` — extends `Repo` to handle installing/uninstalling Python packages from cloned repositories, including support for per-repo install directories and environment variables.
  - `Test(Repo)` — extends `Repo` with a testing abstraction that:
    - Reads per-repo `test` configuration from `pyproject.toml`.
    - Prepares test environments by copying MongoDB-specific settings, migrations, and app configuration into external repos.
    - Builds and runs the appropriate test command (pytest, runtests, or just) with optional module filters, `--keepdb`, and keyword expressions.

- `django_mongodb_cli/repo.py` builds a Typer-based CLI layer on top of these classes. It centralizes common argument patterns via `repo_command`, and each command function (`clone`, `status`, `test`, `patch`, etc.) instantiates and configures the appropriate helper (`Repo`, `Package`, or `Test`).

This separation lets the CLI stay thin while keeping the operational logic (Git, installs, tests) in `utils.py`.

### Project and app scaffolding

- `django_mongodb_cli/project.py` implements the `dm project` subcommands and encapsulates how a Django project is created, configured, and run in a MongoDB-aware way.
  - `add` uses `django-admin startproject` with the bundled `project_template` from `django_mongodb_cli/templates/project_template`.
  - `_create_pyproject_toml` writes a project-specific `pyproject.toml` into each generated project, pre-populating dependencies (`django-mongodb-backend`, `django-debug-toolbar`, `python-webpack-boilerplate`) and pytest/Django settings.
  - `_django_manage_command` wraps `django-admin` for project commands, wiring in `DJANGO_SETTINGS_MODULE` and `PYTHONPATH` using the root `pyproject.toml` configuration and the chosen project name.
  - `_build_mongodb_env` centralizes how `MONGODB_URI` is resolved from CLI options vs environment variables.
  - `run`, `migrate`, `makemigrations`, `manage`, and `su` are thin wrappers around `_django_manage_command` plus MongoDB-specific environment handling.

- `django_mongodb_cli/app.py` provides a similar set of thin wrappers for app-level operations within a Django project:
  - Uses `django-admin startapp --template` with `django_mongodb_cli.templates.app_template` to generate new apps.
  - Provides `makemigrations` and `migrate` wrappers that set `DJANGO_SETTINGS_MODULE` and `PYTHONPATH` appropriately before calling `django-admin`.

- `django_mongodb_cli/frontend.py` specializes app scaffolding for a `frontend` app that also has Node/npm dependencies:
  - `create` scaffolds the app from `templates/frontend_template`.
  - `install` and `run` operate on `package.json` and invoke `npm` commands in the configured frontend directory.

The template directories under `django_mongodb_cli/templates/` (project, app, frontend) are the main extension points for changing the default structure of generated projects/apps.

### Documentation structure

- The Sphinx docs under `docs/source/` mirror the conceptual structure of the tool:
  - `index.rst` introduces "Django MongoDB CLI" and its purpose (testing Django MongoDB Backend, third-party libraries, and MongoDB’s Django fork).
  - `installation.rst` describes the same install flow used above (clone, venv, `pip install -e .`, or `just install`).
  - `usage/` and `third-party-library-support/` subtrees document how to use `dm` with various third-party libraries and test suites.

When modifying or extending CLI behavior, consider updating the corresponding sections in these docs and the `justfile` recipes so that local workflows and documentation stay aligned.
