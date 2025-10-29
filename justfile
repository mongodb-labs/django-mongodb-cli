default:
    echo 'Hello, world!'

# ---------------------------------------- git ----------------------------------------

[group('git')]
git-clone repo:
    @if [ "{{repo}}" = "django" ]; then \
        dm repo clone django --install; \
        dm repo clone django-mongodb-backend --install; \
        dm repo clone django-mongodb-extensions --install; \
        dm repo clone libmongocrypt --install; \
        dm repo clone mongo-python-driver --install; \
    elif [ "{{repo}}" = "langchain" ]; then \
        dm repo clone langchain-mongodb; \
        dm repo clone pymongo-search-utils; \
    elif [ "{{repo}}" = "mongo-arrow" ]; then \
        dm repo clone mongo-arrow --install; \
    else \
        echo "Please provide a valid repo name: django-mongodb-backend, django-mongodb-extensions, or mongo-python-driver"; \
        exit 1; \
    fi

[group('git')]
git-remote repo:
    @if [ "{{repo}}" = "django" ]; then \
        echo "Setting remotes for django-mongodb-backend"; \
        dm repo remote django-mongodb-backend add origin git+ssh://git@github.com/aclark4life/django-mongodb-backend; \
        dm repo remote django-mongodb-backend add upstream git+ssh://git@github.com/mongodb/django-mongodb-backend; \
        dm repo set-default django-mongodb-backend; \
        dm repo fetch django-mongodb-backend; \
        dm repo remote django-mongodb-extensions add origin git+ssh://git@github.com/aclark4life/django-mongodb-extensions; \
        dm repo remote django-mongodb-extensions add upstream git+ssh://git@github.com/mongodb-labs/django-mongodb-extensions; \
        dm repo set-default django-mongodb-extensions; \
        dm repo fetch django-mongodb-extensions; \
        dm repo fetch django-mongodb-extensions; \
    elif [ "{{repo}}" = "pymongo" ]; then \
        echo "Setting remotes for mongo-python-driver"; \
        dm repo remote mongo-python-driver add origin git+ssh://git@github.com/aclark4life/mongo-python-driver; \
        dm repo remote mongo-python-driver add upstream git+ssh://git@github.com/mongodb/mongo-python-driver; \
        dm repo set-default mongo-python-driver; \
        dm repo fetch mongo-python-driver; \
    elif [ "{{repo}}" = "langchain" ]; then \
        echo "Setting remotes for langchain-mongodb"; \
        dm repo remote langchain-mongodb add origin git+ssh://git@github.com/aclark4life/langchain-mongodb; \
        dm repo remote langchain-mongodb add upstream git+ssh://git@github.com/langchain-ai/langchain-mongodb; \
        dm repo set-default langchain-mongodb; \
        dm repo fetch langchain-mongodb; \
        echo "Setting remotes for pymongo-search-utils"; \
        dm repo remote pymongo-search-utils add origin git+ssh://git@github.com/aclark4life/pymongo-search-utils; \
        dm repo remote pymongo-search-utils add upstream git+ssh://git@github.com/mongodb-labs/pymongo-search-utils; \
        dm repo set-default pymongo-search-utils; \
        dm repo fetch pymongo-search-utils; \
    elif [ "{{repo}}" = "mongo-arrow" ]; then \
        echo "Setting remotes for pymongoarrow"; \
        dm repo remote mongo-arrow add origin git+ssh://git@github.com/aclark4life/mongo-arrow; \
        dm repo remote mongo-arrow add upstream git+ssh://git@github.com/mongodb-labs/mongo-arrow; \
        dm repo set-default mongo-arrow; \
        dm repo fetch mongo-arrow; \
    else \
        echo "Please provide a valid repo name: django-mongodb-backend, django-mongodb-extensions, or mongo-python-driver"; \
        exit 1; \
    fi

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
    dm proj migrate
alias m := django-migrate

[group('django')]
django-createsuperuser:
    dm proj su
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
