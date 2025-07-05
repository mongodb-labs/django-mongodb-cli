import click
import os
import subprocess


from .utils import get_management_command


class App:
    def __init__(self):
        self.config = {}

    def set_config(self, key, value):
        self.config[key] = value

    def __repr__(self):
        return f"<App {self}>"


pass_app = click.make_pass_decorator(App)


@click.group(invoke_without_command=True)
@click.pass_context
def app(context):
    """
    Create Django apps configured to test django-mongodb-backend.
    """
    context.obj = App()

    # Show help only if no subcommand is invoked
    if context.invoked_subcommand is None:
        click.echo(context.get_help())
        context.exit()


@app.command()
@click.argument("app_name", required=False, default="mongo_app")
def start(app_name):
    """Run startapp command with the template from src/django-mongodb-app."""

    click.echo("Running startapp.")
    command = get_management_command("startapp")
    subprocess.run(
        command
        + [
            app_name,
            "--template",
            os.path.join("src", "django-project-templates", "app_template"),
        ],
    )
