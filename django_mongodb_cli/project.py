import signal
import typer
import shutil
from pathlib import Path
import subprocess
import importlib.resources as resources
import os
import sys
import random
from .utils import Repo

project = typer.Typer(help="Manage Django projects.")

# Constants for random name generation
ADJECTIVES = [
    "happy",
    "sunny",
    "clever",
    "brave",
    "calm",
    "bright",
    "swift",
    "gentle",
    "mighty",
    "noble",
    "quiet",
    "wise",
    "bold",
    "keen",
    "lively",
    "merry",
    "proud",
    "quick",
    "smart",
    "strong",
]
NOUNS = [
    "panda",
    "eagle",
    "tiger",
    "dragon",
    "phoenix",
    "falcon",
    "wolf",
    "bear",
    "lion",
    "hawk",
    "owl",
    "fox",
    "deer",
    "otter",
    "seal",
    "whale",
    "shark",
    "raven",
    "cobra",
    "lynx",
]


def generate_random_project_name():
    """Generate a random project name using adjectives and nouns."""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adjective}_{noun}"


@project.command("add")
def add_project(
    name: str = typer.Argument(
        None, help="Project name (optional if --random is used)"
    ),
    directory: Path = Path("."),
    add_frontend: bool = typer.Option(
        True,
        "--add-frontend/--no-frontend",
        "-f/-F",
        help="Add frontend (default: True)",
    ),
    random_name: bool = typer.Option(
        False,
        "--random",
        "-r",
        help="Generate a random project name. If both name and --random are provided, the name takes precedence.",
    ),
):
    """
    Create a new Django project using bundled templates.
    Frontend is added by default. Use --no-frontend to skip frontend creation.

    Examples:
        dm project add myproject          # Create with explicit name (includes frontend)
        dm project add myproject --no-frontend  # Create without frontend
        dm project add --random           # Create with random name (includes frontend)
        dm project add -r                 # Short form
    """
    # Handle random name generation
    if random_name:
        if name is not None:
            typer.echo(
                "⚠️  Both a project name and --random flag were provided. Using the provided name.",
                err=True,
            )
        else:
            name = generate_random_project_name()
            typer.echo(f"🎲 Generated random project name: {name}")
    elif name is None:
        typer.echo(
            "❌ Project name is required. Provide a name or use --random flag.",
            err=True,
        )
        raise typer.Exit(code=1)

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

        # Run django-admin in a way that surfaces a clean, user-friendly error
        # instead of a full Python traceback when Django is missing or
        # misconfigured in the current environment.
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            typer.echo(
                "❌ 'django-admin' command not found. Make sure Django is installed "
                "in this environment and that 'django-admin' is on your PATH.",
                err=True,
            )
            raise typer.Exit(code=1)

        if result.returncode != 0:
            # Try to show a concise reason (e.g. "ModuleNotFoundError: No module named 'django'")
            reason = None
            if result.stderr:
                lines = [
                    line.strip() for line in result.stderr.splitlines() if line.strip()
                ]
                if lines:
                    reason = lines[-1]

            typer.echo(
                "❌ Failed to create project using django-admin. "
                "This usually means Django is not installed or is misconfigured "
                "in the current Python environment.",
                err=True,
            )
            if reason:
                typer.echo(f"   Reason: {reason}", err=True)

            raise typer.Exit(code=result.returncode)

    # Add pyproject.toml after project creation
    _create_pyproject_toml(project_path, name)

    # Create frontend by default (unless --no-frontend is specified)
    if add_frontend:
        typer.echo(f"🎨 Adding frontend to project '{name}'...")
        try:
            # Call the internal frontend create helper
            _add_frontend(name, directory)
        except Exception as e:
            typer.echo(
                f"⚠️  Project created successfully, but frontend creation failed: {e}",
                err=True,
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
    "django-debug-toolbar",
]
test = [
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
    """Delete a Django project by name.

    This will first attempt to uninstall the project package using pip in the
    current Python environment, then remove the project directory.
    """
    target = directory / name

    if not target.exists() or not target.is_dir():
        typer.echo(f"❌ Project {name} does not exist.", err=True)
        return

    # Try to uninstall the package from the current environment before
    # removing the project directory. Failures here are non-fatal so that
    # filesystem cleanup still proceeds.
    uninstall_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", name]
    typer.echo(f"📦 Uninstalling project package '{name}' with pip")
    try:
        result = subprocess.run(uninstall_cmd, check=False)
        if result.returncode != 0:
            typer.echo(
                f"⚠️ pip uninstall exited with code {result.returncode}. "
                "Proceeding to remove project files.",
                err=True,
            )
    except FileNotFoundError:
        typer.echo(
            "⚠️ Could not run pip to uninstall the project package. "
            "Proceeding to remove project files.",
            err=True,
        )

    shutil.rmtree(target)
    typer.echo(f"🗑️ Removed project {name}")


@project.command("install")
def install_project(name: str, directory: Path = Path(".")):
    """Install a generated Django project by running ``pip install .`` in its directory.

    If a frontend directory exists, also installs npm dependencies.

    Example:
        dm project install qe
    """
    project_path = directory / name

    if not project_path.exists() or not project_path.is_dir():
        typer.echo(
            f"❌ Project '{name}' does not exist at {project_path}.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"📦 Installing project '{name}' with pip (cwd={project_path})")

    # Use the current Python interpreter to ensure we install into the
    # same environment that is running the CLI.
    cmd = [sys.executable, "-m", "pip", "install", "."]
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            check=False,
        )
    except FileNotFoundError:
        typer.echo(
            "❌ Could not run pip. Make sure Python and pip are available in this environment.",
            err=True,
        )
        raise typer.Exit(code=1)

    if result.returncode != 0:
        typer.echo(
            f"❌ pip install failed with exit code {result.returncode}.",
            err=True,
        )
        raise typer.Exit(code=result.returncode)

    typer.echo(f"✅ Successfully installed project '{name}'")

    # Check if frontend exists and install npm dependencies
    frontend_path = project_path / "frontend"
    if frontend_path.exists() and (frontend_path / "package.json").exists():
        typer.echo("🎨 Frontend detected, installing npm dependencies...")
        try:
            _install_npm(name, directory=directory)
        except typer.Exit:
            typer.echo(
                "⚠️  Frontend npm installation failed, but project installation succeeded.",
                err=True,
            )
        except Exception as e:
            typer.echo(
                f"⚠️  Unexpected error during frontend installation: {e}",
                err=True,
            )


def _django_manage_command(
    name: str,
    directory: Path,
    *args: str,
    extra_env: dict | None = None,
    frontend: bool = False,
    settings: str | None = None,
):
    """
    Internal helper to call django-admin with the right environment.

    Args:
        name: Project name
        directory: Parent directory containing the project
        args: Arguments to pass to django-admin
        extra_env: Extra environment variables
        frontend: Whether to run frontend alongside
        settings: Optional settings configuration name (e.g., 'site1', 'site2')
    """
    repo = Repo()
    project_path = directory / name
    if not project_path.exists():
        typer.echo(f"❌ Project '{name}' does not exist at {project_path}", err=True)
        raise typer.Exit(code=1)

    parent_dir = project_path.parent.resolve()
    env = os.environ.copy()

    # Get the settings path using the new method
    try:
        settings_path = repo.get_project_settings(settings)
    except ValueError as e:
        typer.echo(f"❌ {e}", err=True)
        raise typer.Exit(code=1)

    env["DJANGO_SETTINGS_MODULE"] = f"{name}.{settings_path}"
    env["PYTHONPATH"] = str(name) + os.pathsep + env.get("PYTHONPATH", "")
    typer.echo(f"🔧 Using DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}")
    if extra_env:
        env.update(extra_env)

    if frontend:
        # Ensure frontend is installed
        try:
            _install_npm(name, directory=parent_dir)
        except typer.Exit:
            typer.echo(
                "⚠️  Frontend installation failed",
                err=True,
            )
            # Continue anyway - frontend might already be installed

        # Start frontend process in background
        frontend_path = project_path / "frontend"
        frontend_proc = subprocess.Popen(
            ["npm", "run", "watch"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

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
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'site1', 'site2')",
    ),
):
    """
    Run a Django project using ``django-admin`` instead of ``manage.py``,
    with ``MONGODB_URI`` set in the environment if provided.

    If a frontend directory exists, it will be run automatically alongside the Django server.

    Examples:
        dm project run myproject
        dm project run myproject --settings site1
        dm project run myproject -s site2
    """
    project_path = directory / name

    # Check if frontend exists
    frontend_path = project_path / "frontend"
    has_frontend = frontend_path.exists() and (frontend_path / "package.json").exists()

    typer.echo(f"🚀 Running project '{name}' on http://{host}:{port}")
    _django_manage_command(
        name,
        directory,
        "runserver",
        f"{host}:{port}",
        extra_env=_build_mongodb_env(mongodb_uri),
        frontend=has_frontend,
        settings=settings,
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
    database: str = typer.Option(
        None,
        help="Specify the database to migrate.",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'site1', 'site2')",
    ),
):
    """
    Run Django migrations using django-admin instead of manage.py.

    Examples:
        dm project migrate myproject
        dm project migrate myproject --settings site1
        dm project migrate myproject auth
    """
    cmd = ["migrate"]
    if app_label:
        cmd.append(app_label)
    if migration_name:
        cmd.append(migration_name)
    if database:
        cmd.append(f"--database={database}")
    typer.echo(f"📦 Applying migrations for project '{name}'")
    _django_manage_command(
        name,
        directory,
        *cmd,
        extra_env=_build_mongodb_env(mongodb_uri),
        settings=settings,
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
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'site1', 'site2')",
    ),
):
    """
    Create new Django migrations using django-admin instead of manage.py.

    Examples:
        dm project makemigrations myproject
        dm project makemigrations myproject --settings site1
        dm project makemigrations myproject myapp
    """
    cmd = ["makemigrations"]
    if app_label:
        cmd.append(app_label)

    typer.echo(f"🛠️ Making migrations for project '{name}'")
    _django_manage_command(
        name,
        directory,
        *cmd,
        extra_env=_build_mongodb_env(mongodb_uri),
        settings=settings,
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
    database: str = typer.Option(
        None,
        help="Specify the database to use.",
    ),
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'site1', 'site2')",
    ),
):
    """
    Run any django-admin command for a project.

    Examples:
        dm project manage mysite shell
        dm project manage mysite createsuperuser
        dm project manage mysite --mongodb-uri mongodb+srv://user:pwd@cluster
        dm project manage mysite --settings site1 shell
        dm project manage mysite
    """
    if args is None:
        args = []

    if mongodb_uri:
        typer.echo(f"🔗 Using MongoDB URI: {mongodb_uri}")
        # You could pass this into your Django settings or set an environment var
        import os

        os.environ["MONGODB_URI"] = mongodb_uri

    if database:
        args.append(f"--database={database}")

    if command:
        typer.echo(f"⚙️  Running django-admin {command} {' '.join(args)} for '{name}'")
        _django_manage_command(name, directory, command, *args, settings=settings)
    else:
        typer.echo(f"ℹ️  Running django-admin with no arguments for '{name}'")
        _django_manage_command(name, directory, settings=settings)


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
    settings: str = typer.Option(
        None,
        "--settings",
        "-s",
        help="Settings configuration name to use (e.g., 'site1', 'site2')",
    ),
):
    """
    Create a Django superuser with no interaction required, using django-admin instead of manage.py.

    Examples:
        dm project su myproject
        dm project su myproject --settings site1
        dm project su myproject -u myuser -p mypass
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
        settings=settings,
    )


# Internal helper functions for frontend management


def _add_frontend(
    project_name: str,
    directory: Path = Path("."),
):
    """
    Internal helper to create a frontend app inside an existing project.
    """
    project_path = directory / project_name
    name = "frontend"
    if not project_path.exists() or not project_path.is_dir():
        typer.echo(f"❌ Project '{project_name}' not found at {project_path}", err=True)
        raise typer.Exit(code=1)
    # Destination for new app
    app_path = project_path / name
    if app_path.exists():
        typer.echo(
            f"❌ App '{name}' already exists in project '{project_name}'", err=True
        )
        raise typer.Exit(code=1)
    typer.echo(f"📦 Creating app '{name}' in project '{project_name}'")
    # Locate the Django app template directory in package resources
    with resources.path(
        "django_mongodb_cli.templates", "frontend_template"
    ) as template_path:
        cmd = [
            "django-admin",
            "startapp",
            "--template",
            str(template_path),
            name,
            str(project_path),
        ]
        subprocess.run(cmd, check=True)


def _remove_frontend(project_name: str, directory: Path = Path(".")):
    """
    Internal helper to remove a frontend app from a project.
    """
    name = "frontend"
    target = directory / project_name / name
    if target.exists() and target.is_dir():
        shutil.rmtree(target)
        typer.echo(f"🗑️ Removed app '{name}' from project '{project_name}'")
    else:
        typer.echo(f"❌ App '{name}' does not exist in '{project_name}'", err=True)


def _install_npm(
    project_name: str,
    frontend_dir: str = "frontend",
    directory: Path = Path("."),
    clean: bool = False,
):
    """
    Internal helper to install npm dependencies in the frontend directory.
    """
    project_path = directory / project_name
    if not project_path.exists():
        typer.echo(
            f"❌ Project '{project_name}' does not exist at {project_path}", err=True
        )
        raise typer.Exit(code=1)

    frontend_path = project_path / frontend_dir
    if not frontend_path.exists():
        typer.echo(
            f"❌ Frontend directory '{frontend_dir}' not found at {frontend_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    package_json = frontend_path / "package.json"
    if not package_json.exists():
        typer.echo(f"❌ package.json not found in {frontend_path}", err=True)
        raise typer.Exit(code=1)

    if clean:
        typer.echo(f"🧹 Cleaning node_modules and package-lock.json in {frontend_path}")
        node_modules = frontend_path / "node_modules"
        package_lock = frontend_path / "package-lock.json"

        if node_modules.exists():
            shutil.rmtree(node_modules)
            typer.echo("  ✓ Removed node_modules")

        if package_lock.exists():
            package_lock.unlink()
            typer.echo("  ✓ Removed package-lock.json")

    typer.echo(f"📦 Installing npm dependencies in {frontend_path}")

    try:
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        typer.echo("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ npm install failed with exit code {e.returncode}", err=True)
        raise typer.Exit(code=e.returncode)
    except FileNotFoundError:
        typer.echo(
            "❌ npm not found. Please ensure Node.js and npm are installed.", err=True
        )
        raise typer.Exit(code=1)


def _run_npm(
    project_name: str,
    frontend_dir: str = "frontend",
    directory: Path = Path("."),
    script: str = "watch",
):
    """
    Internal helper to run npm script in the frontend directory.
    """
    project_path = directory / project_name
    if not project_path.exists():
        typer.echo(
            f"❌ Project '{project_name}' does not exist at {project_path}", err=True
        )
        raise typer.Exit(code=1)

    frontend_path = project_path / frontend_dir
    if not frontend_path.exists():
        typer.echo(
            f"❌ Frontend directory '{frontend_dir}' not found at {frontend_path}",
            err=True,
        )
        raise typer.Exit(code=1)

    package_json = frontend_path / "package.json"
    if not package_json.exists():
        typer.echo(f"❌ package.json not found in {frontend_path}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"🚀 Running 'npm run {script}' in {frontend_path}")

    try:
        subprocess.run(["npm", "run", script], cwd=frontend_path, check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ npm command failed with exit code {e.returncode}", err=True)
        raise typer.Exit(code=e.returncode)
    except FileNotFoundError:
        typer.echo(
            "❌ npm not found. Please ensure Node.js and npm are installed.", err=True
        )
        raise typer.Exit(code=1)
