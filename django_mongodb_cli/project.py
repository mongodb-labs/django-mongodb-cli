import signal
import typer
import shutil
from pathlib import Path
import subprocess
import importlib.resources as resources
import os
from .frontend import add_frontend as _add_frontend
from .utils import Repo

project = typer.Typer(help="Manage Django projects.")


@project.command("add")
def add_project(
    name: str,
    directory: Path = Path("."),
    add_frontend: bool = typer.Option(
        False, "--add-frontend", "-f", help="Add frontend"
    ),
):
    """
    Create a new Django project using bundled templates.
    """
    project_path = directory / name
    if project_path.exists():
        typer.echo(f"❌ Project '{name}' already exists at {project_path}", err=True)
        raise typer.Exit(code=1)

    with resources.path(
        "django_mongodb_cli.templates", "project_template"
    ) as template_path:
        cmd = [
            "django-admin",
            "startproject",
            "--template",
            str(template_path),
            name,
        ]
        typer.echo(f"📦 Creating project: {name}")
        subprocess.run(cmd, check=True)

    # Add pyproject.toml after project creation
    _create_pyproject_toml(project_path, name)

    # Conditionally create frontend if -f flag is set
    if add_frontend:
        typer.echo(f"🎨 Adding frontend to project '{name}'...")
        try:
            # Call the frontend create command
            _add_frontend(name, project_path)
        except Exception as e:
            typer.echo(
                f"⚠️  Project created successfully, but frontend creation failed: {e}",
                err=True,
            )
            typer.echo(
                "You can manually add the frontend later using: frontend create frontend <project_name>"
            )


def _create_pyproject_toml(project_path: Path, project_name: str):
    """Create a pyproject.toml file for the Django project."""
    pyproject_content = f"""[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A Django project built with Django MongoDB CLI"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
dependencies = [
    "django-debug-toolbar",
    "django-mongodb-backend",
    "python-webpack-boilerplate",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-django",
    "ruff",
]
encryption = [
    "pymongocrypt",
]

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "{project_name}.settings.base"
python_files = ["tests.py", "test_*.py", "*_tests.py"]

[tool.setuptools]
packages = ["{project_name}"]
"""

    pyproject_path = project_path / "pyproject.toml"
    try:
        pyproject_path.write_text(pyproject_content)
        typer.echo(f"✅ Created pyproject.toml for '{project_name}'")
    except Exception as e:
        typer.echo(f"⚠️  Failed to create pyproject.toml: {e}", err=True)


@project.command("remove")
def remove_project(name: str, directory: Path = Path(".")):
    """
    Delete a Django project by name.
    """
    target = directory / name
    if target.exists() and target.is_dir():
        shutil.rmtree(target)
        typer.echo(f"🗑️ Removed project {name}")
    else:
        typer.echo(f"❌ Project {name} does not exist.", err=True)


def _django_manage_command(
    name: str,
    directory: Path,
    *args: str,
    extra_env: dict | None = None,
    frontend: bool = False,
):
    """
    Internal helper to call django-admin with the right environment.
    """
    repo = Repo()
    project_path = directory / name
    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' does not exist at {project_path}", err=True)
        raise typer.Exit(code=1)

    parent_dir = project_path.parent.resolve()
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = (
        f"{name}.{repo._tool_cfg.get('project', {}).get('settings', {}).get('path', 'settings.base')}"
    )
    env["PYTHONPATH"] = str(name) + os.pathsep + env.get("PYTHONPATH", "")
    typer.echo(f"🔧 Using DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}")
    if extra_env:
        env.update(extra_env)

    if frontend:
        # Ensure frontend is installed
        subprocess.run(["dm", "frontend", "install", name])

        # Start frontend process in background
        frontend_proc = subprocess.Popen(["dm", "frontend", "run", name])

        # Handle CTRL-C to kill both processes
        def signal_handler(signum, frame):
            frontend_proc.terminate()
            raise KeyboardInterrupt

        signal.signal(signal.SIGINT, signal_handler)

        try:
            subprocess.run(["django-admin", *args], cwd=parent_dir, env=env, check=True)
        except KeyboardInterrupt:
            pass
        finally:
            if frontend_proc.poll() is None:
                frontend_proc.terminate()
    else:
        # Original behavior - just run django-admin

        try:
            subprocess.run(["django-admin", *args], cwd=parent_dir, env=env, check=True)

        except subprocess.CalledProcessError as e:
            typer.echo(f"❌ Command failed with exit code {e.returncode}", err=True)
            raise typer.Exit(code=e.returncode)


def _build_mongodb_env(mongodb_uri: str | None):
    """
    Returns a dict with MONGODB_URI if provided or found in environment.
    """
    if not mongodb_uri:
        mongodb_uri = os.getenv("MONGODB_URI")  # fallback to existing env var

    extra_env = {}
    if mongodb_uri:
        extra_env["MONGODB_URI"] = mongodb_uri
        typer.echo(f"🔗 Using MONGODB_URI: {mongodb_uri}")
    else:
        typer.echo("⚠️ MONGODB_URI not provided. Using Django's default DB settings.")
    return extra_env if extra_env else None


@project.command("run")
def run_project(
    name: str,
    directory: Path = Path("."),
    host: str = "127.0.0.1",
    port: int = 8000,
    mongodb_uri: str = typer.Option(
        None,
        help="Optional MongoDB connection URI. Falls back to $MONGODB_URI if not provided.",
    ),
    frontend: bool = typer.Option(False, "-f", "--frontend", help="Run frontend"),
):
    """
    Run a Django project using django-admin instead of manage.py,
    with MONGODB_URI set in the environment if provided.
    """
    typer.echo(f"🚀 Running project '{name}' on http://{host}:{port}")
    _django_manage_command(
        name,
        directory / name,
        "runserver",
        f"{host}:{port}",
        extra_env=_build_mongodb_env(mongodb_uri),
        frontend=frontend,
    )


@project.command("migrate")
def migrate_project(
    name: str,
    directory: Path = Path("."),
    app_label: str = typer.Argument(None),
    migration_name: str = typer.Argument(None),
    mongodb_uri: str = typer.Option(
        None,
        help="Optional MongoDB connection URI. Falls back to $MONGODB_URI if not provided.",
    ),
):
    """
    Run Django migrations using django-admin instead of manage.py.
    """
    cmd = ["migrate"]
    directory = Path(name)
    if app_label:
        cmd.append(app_label)
    if migration_name:
        cmd.append(migration_name)

    typer.echo(f"📦 Applying migrations for project '{name}'")
    _django_manage_command(
        name, directory, *cmd, extra_env=_build_mongodb_env(mongodb_uri)
    )


@project.command("makemigrations")
def makemigrations_project(
    name: str,
    directory: Path = Path("."),
    app_label: str = typer.Argument(None),
    mongodb_uri: str = typer.Option(
        None,
        help="Optional MongoDB connection URI. Falls back to $MONGODB_URI if not provided.",
    ),
):
    """
    Create new Django migrations using django-admin instead of manage.py.
    """
    cmd = ["makemigrations"]
    if app_label:
        cmd.append(app_label)

    typer.echo(f"🛠️ Making migrations for project '{name}'")
    _django_manage_command(
        name, directory, *cmd, extra_env=_build_mongodb_env(mongodb_uri)
    )


@project.command("manage")
def manage_command(
    name: str,
    directory: Path = Path("."),
    command: str = typer.Argument(None),
    args: list[str] = typer.Argument(None),
    mongodb_uri: str = typer.Option(
        None, "--mongodb-uri", help="MongoDB connection URI"
    ),
):
    """
    Run any django-admin command for a project.

    Examples:
        dm project manage mysite shell
        dm project manage mysite createsuperuser
        dm project manage mysite --mongodb-uri mongodb+srv://user:pwd@cluster
        dm project manage mysite
    """
    if args is None:
        args = []

    if mongodb_uri:
        typer.echo(f"🔗 Using MongoDB URI: {mongodb_uri}")
        # You could pass this into your Django settings or set an environment var
        import os

        os.environ["MONGODB_URI"] = mongodb_uri

    if command:
        typer.echo(f"⚙️  Running django-admin {command} {' '.join(args)} for '{name}'")
        _django_manage_command(name, directory, command, *args)
    else:
        typer.echo(f"ℹ️  Running django-admin with no arguments for '{name}'")
        _django_manage_command(name, directory)


@project.command("su")
def create_superuser(
    name: str,
    directory: Path = Path("."),
    username: str = typer.Option(
        "admin", "--username", "-u", help="Superuser username"
    ),
    password: str = typer.Option(
        "admin", "--password", "-p", help="Superuser password"
    ),
    email: str = typer.Option(
        None,
        "--email",
        "-e",
        help="Superuser email (defaults to $PROJECT_EMAIL if set)",
    ),
    mongodb_uri: str = typer.Option(
        None,
        help="Optional MongoDB connection URI. Falls back to $MONGODB_URI if not provided.",
    ),
):
    """
    Create a Django superuser with no interaction required, using django-admin instead of manage.py.
    """
    if not email:
        email = os.getenv("PROJECT_EMAIL", "admin@example.com")

    typer.echo(f"👑 Creating Django superuser '{username}' for project '{name}'")

    extra_env = _build_mongodb_env(mongodb_uri) or {}
    extra_env["DJANGO_SUPERUSER_PASSWORD"] = password

    _django_manage_command(
        name,
        directory,
        "createsuperuser",
        "--noinput",
        f"--username={username}",
        f"--email={email}",
        extra_env=extra_env,
    )
