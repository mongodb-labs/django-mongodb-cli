import click
import os
import subprocess


from .utils import get_management_command


@click.command()
def runserver():
    """Start the Django development server."""

    if os.environ.get("MONGODB_URI"):
        click.echo(os.environ["MONGODB_URI"])

    command = get_management_command()

    # Start npm install
    subprocess.run(["npm", "install"], cwd="frontend")

    # Start npm run watch
    npm_process = subprocess.Popen(["npm", "run", "watch"], cwd="frontend")

    # Start django-admin runserver
    django_process = subprocess.Popen(command + ["runserver"])

    # Wait for both processes to complete
    npm_process.wait()
    django_process.wait()
