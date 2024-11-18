import click
import os
import subprocess


from .utils import get_management_command


@click.command()
def createsuperuser():
    """Create a superuser with the username 'admin' and the email from git config."""
    try:
        user_email = subprocess.check_output(
            ["git", "config", "user.email"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        click.echo("Error: Unable to retrieve the user email from git config.")
        return

    os.environ["DJANGO_SUPERUSER_PASSWORD"] = "admin"

    if os.environ.get("MONGODB_URI"):
        click.echo(os.environ["MONGODB_URI"])
    click.echo(f"User email: {user_email}")

    command = get_management_command("createsuperuser")

    subprocess.run(
        command
        + [
            "--noinput",
            "--username=admin",
            f"--email={user_email}",
        ]
    )
