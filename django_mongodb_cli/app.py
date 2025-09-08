import typer
import shutil
from pathlib import Path
import subprocess
import importlib.resources as resources
import os

app = typer.Typer(help="Manage Django apps.")


@app.command("create")
def add_app(name: str, project_name: str, directory: Path = Path(".")):
    """
    Create a new Django app inside an existing project using bundled templates.
    """
    project_path = directory / project_name
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
        "django_mongodb_cli.templates", "app_template"
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


@app.command("remove")
def remove_app(name: str, project_name: str, directory: Path = Path(".")):
    """
    Remove a Django app from a project.
    """
    target = directory / project_name / name
    if target.exists() and target.is_dir():
        shutil.rmtree(target)
        typer.echo(f"🗑️ Removed app '{name}' from project '{project_name}'")
    else:
        typer.echo(f"❌ App '{name}' does not exist in '{project_name}'", err=True)


def _django_admin_cmd(project_name: str, directory: Path, *args: str):
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
    env["DJANGO_SETTINGS_MODULE"] = f"{project_name}.settings"
    env["PYTHONPATH"] = str(parent_dir) + os.pathsep + env.get("PYTHONPATH", "")

    subprocess.run(["django-admin", *args], cwd=parent_dir, env=env, check=True)


@app.command("makemigrations")
def makemigrations_app(project_name: str, app_label: str, directory: Path = Path(".")):
    """
    Run makemigrations for the given app inside a project.
    """
    typer.echo(f"🛠️ Making migrations for app '{app_label}' in project '{project_name}'")
    _django_admin_cmd(project_name, directory, "makemigrations", app_label)


@app.command("migrate")
def migrate_app(
    project_name: str,
    app_label: str = typer.Argument(None),
    migration_name: str = typer.Argument(None),
    directory: Path = Path("."),
):
    """
    Apply migrations for the given app inside a project.
    """
    cmd = ["migrate"]
    if app_label:
        cmd.append(app_label)
    if migration_name:
        cmd.append(migration_name)

    typer.echo(
        f"📦 Applying migrations for {app_label or 'all apps'} in '{project_name}'"
    )
    _django_admin_cmd(project_name, directory, *cmd)
