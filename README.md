# django-mongodb-cli

## About

For testing [django-mongodb-backend](https://github.com/mongodb-labs/django-mongodb-backend)
with [MongoDB's Django fork](https://github.com/mongodb-forks/django) and [third party libraries](#third-party-libraries).

> [!NOTE]
> [MongoDB's Django fork](https://github.com/mongodb-forks/django) is for *testing* [django-mongodb-backend](https://github.com/mongodb-labs/django-mongodb-backend)
> and is not a requirement for *using* [django-mongodb-backend](https://github.com/mongodb-labs/django-mongodb-backend).

## Installation

```bash
git clone https://github.com/mongodb-labs/django-mongodb-cli
cd django-mongodb-cli
python -m venv .venv
source .venv/bin/activate
just install
```

## Usage

```
Usage: dm [OPTIONS] COMMAND [ARGS]...

  Django MongoDB CLI

Options:
  --help  Show this message and exit.

Commands:
  repo          Run Django fork and third-party library tests.
  startproject  Run `startproject` with custom templates.
```
