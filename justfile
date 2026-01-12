default:
    echo 'Hello, world!'

# ---------------------------------------- git ----------------------------------------
# Use `dm repo clone --group <group>` to clone a group of repositories
# Use `dm repo remote setup --group <group>` to setup remotes for a group
# Use `dm repo clone --list-groups` to see available groups

[group('git')]
git-clone repo:
    @dm repo clone --group {{repo}} --install

[group('git')]
git-remote repo:
    @dm repo remote setup --group {{repo}}
    @dm repo set-default --group {{repo}}


p:
    nvim pyproject.toml

# ---------------------------------------- django ----------------------------------------

[group('django')]
django-open:
    open http://localhost:8000
alias o := django-open

[group('django')]
django-runserver:
    dm proj run
alias s := django-runserver

[group('django')]
django-migrate:
    dm project migrate
alias m := django-migrate

[group('django')]
django-createsuperuser:
    dm project su
alias su := django-createsuperuser

# ---------------------------------------- mongodb ----------------------------------------

[group('mongodb')]
drop db:
    @if [ -z "{{ db }}" ]; then \
        echo "Please provide a database name using the 'db' parameter."; \
        exit 1; \
    else \
        echo "Dropping database: {{ db }}"; \
        mongosh --eval "db.dropDatabase()"; \
    fi
alias d := drop

# ---------------------------------------- python ----------------------------------------

# install python dependencies and activate pre-commit hooks
[group('python')]
pip-install: check-venv
    # brew install libxml2 libxmlsec1 mongo-c-driver mongo-c-driver@1 pkg-config
    # pip install lxml==5.3.2 --no-binary :all:
    pip install -U pip
    pip install -e .
    pre-commit install

# ensure virtual environment is active
[group('python')]
check-venv:
    #!/bin/bash
    PYTHON_PATH=$(which python)
    if [[ $PYTHON_PATH == *".venv/bin/python" ]]; then
      echo "Virtual environment is active."
    else
      echo "Virtual environment is not active."
      exit 1
    fi

[group('python')]
install: pip-install
alias i := install

# ---------------------------------------- sphinx ----------------------------------------

[group('sphinx')]
sphinx-build:
    sphinx-build -b html docs/source docs/_build
alias b := sphinx-build

[group('sphinx')]
sphinx-autobuild:
    # cd docs/_build && python -m http.server
    sphinx-autobuild docs/source docs/_build
alias ab := sphinx-autobuild

[group('sphinx')]
sphinx-clean:
    rm -rvf docs/_build
alias sc := sphinx-clean

[group('sphinx')]
sphinx-open:
    open docs/_build/index.html
alias so := sphinx-open

# ---------------------------------------- jira ----------------------------------------

[group('jira')]
INTPYTHON-527:
    python jira/INTPYTHON-527.py
alias q := INTPYTHON-527

[group('jira')]
PYTHON-5564 group="" package="":
    python3.10 -m venv .venv
    python3.10 -m pip install -U pip
    python3.10 -m pip install requests src/mongo-python-driver
    if [ -z "{{group}}" ] && [ -z "{{package}}" ]; then \
        python3.10 jira/PYTHON-5564.py; \
    elif [ -n "{{group}}" ] && [ -z "{{package}}" ]; then \
        python3.10 jira/PYTHON-5564.py --group "{{group}}"; \
    elif [ -z "{{group}}" ] && [ -n "{{package}}" ]; then \
        python3.10 jira/PYTHON-5564.py --package "{{package}}"; \
    else \
        python3.10 jira/PYTHON-5564.py --group "{{group}}" --package "{{package}}"; \
    fi
