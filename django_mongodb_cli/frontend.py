import typer
import shutil
from pathlib import Path
import subprocess
import importlib.resources as resources
import os

frontend = typer.Typer(help="Manage Django apps.")


@frontend.command("create")
def add_frontend(
    project_name: str,
    directory: Path = Path("."),
):
    """
    Create a new Django app inside an existing project using bundled templates.
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
            directory,
        ]
        subprocess.run(cmd, check=True)


@frontend.command("remove")
def remove_frontend(project_name: str, directory: Path = Path(".")):
    """
    Remove a Django app from a project.
    """
    name = "frontend"
    target = directory / project_name / name
    if target.exists() and target.is_dir():
        shutil.rmtree(target)
        typer.echo(f"🗑️ Removed app '{name}' from project '{project_name}'")
    else:
        typer.echo(f"❌ App '{name}' does not exist in '{project_name}'", err=True)


@frontend.command("install")
def install_npm(
    project_name: str,
    frontend_dir: str = "frontend",
    directory: Path = Path("."),
    clean: bool = typer.Option(
        False,
        "--clean",
        help="Remove node_modules and package-lock.json before installing",
    ),
):
    """
    Install npm dependencies in the frontend directory.
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


@frontend.command("run")
def run_npm(
    project_name: str,
    frontend_dir: str = "frontend",
    directory: Path = Path("."),
    script: str = typer.Option("watch", help="NPM script to run (default: watch)"),
):
    """
    Run npm script in the frontend directory.
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


def django_admin_cmd(project_name: str, directory: Path, *args: str):
    """
    Internal helper to run `django-admin` with project's DJANGO_SETTINGS_MODULE.
    """
    project_path = directory / project_name
    if not project_path.exists():
        typer.echo(
            f"❌ Project '{project_name}' does not exist at {project_path}", err=True
        )
        raise typer.Exit(code=1)
    parent_dir = project_path.parent.resolve()
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = f"{project_name}.settings.base"
    env["PYTHONPATH"] = str(parent_dir) + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.run(["django-admin", *args], cwd=parent_dir, env=env, check=True)
