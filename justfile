default:
    echo 'Hello, world!'

install: pip-install git-clone dev-install
alias i := install

dev-install:
    dm repo install django-mongodb-backend
    dm repo install django-mongodb-extensions
    dm repo install mongo-python-driver


demo:
    dm repo test django queries_
    dm repo test django-filter tests.test_filters
    dm repo test django-debug-toolbar
    dm repo test django-allauth allauth/account/tests
alias d := demo

# ---------------------------------------- git ----------------------------------------

[group('git')]
git-clone:
    dm repo clone django-mongodb-app
    dm repo clone django-mongodb-backend
    dm repo clone django-mongodb-extensions
    dm repo clone django-mongodb-project
    dm repo clone django-mongodb-templates
    dm repo clone mongo-python-driver

# ---------------------------------------- django ----------------------------------------

[group('django')]
django-open:
    open http://localhost:8000
alias o := django-open

[group('django')]
django-serve:
    dm runserver
alias s := django-serve

[group('django')]
django-migrate:
    dm manage migrate
alias m := django-migrate

[group('django')]
django-createsuperuser:
    dm createsuperuser
alias su := django-createsuperuser

# ---------------------------------------- mongodb ----------------------------------------

[group('mongodb')]
db-init:
    # mongosh `echo ${MONGODB_URI}` --eval 'db.dropDatabase()'
    mongosh `echo mongodb://0.0.0.0/backend` --eval 'db.dropDatabase()'

# ---------------------------------------- python ----------------------------------------

# install python dependencies and activate pre-commit hooks
[group('python')]
pip-install: check-venv
    brew install libxml2 libxmlsec1 pkg-config
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

[group('npm')]
npm-install:
    npm install

# ---------------------------------------- sphinx ----------------------------------------

[group('sphinx')]
sphinx-build:
    sphinx-build -b html docs/source docs/_build
alias b := sphinx-build

[group('sphinx')]
sphinx-serve:
    cd docs/_build && python -m http.server
alias ss := sphinx-serve
