import click
import os
import shutil
import subprocess


@click.group()
def cli():
    pass


@click.command()
@click.argument("modules", nargs=-1)
@click.option("-k", "--keyword", help="Filter tests by keyword")
@click.option(
    "-l", "--list-tests", default=False, is_flag=True, help="List available tests"
)
def test(modules, keyword, list_tests):
    """
    Run tests for specified modules with an optional keyword filter.
    """
    if list_tests:
        click.echo(subprocess.run(["ls", os.path.join("src", "django", "tests")]))
        click.echo(
            subprocess.run(["ls", os.path.join("src", "django-mongodb", "tests")])
        )
        exit()

    shutil.copyfile(
        "src/django-mongodb/.github/workflows/mongodb_settings.py",
        "src/django/tests/mongodb_settings.py",
    )

    command = ["src/django/tests/runtests.py"]
    command.extend(["--settings", "mongodb_settings"])
    command.extend(["--parallel", "1"])
    command.extend(["--verbosity", "3"])
    command.extend(["--debug-sql"])

    # Add modules to the command
    command.extend(modules)

    # Add keyword filter if provided
    if keyword:
        command.extend(["-k", keyword])

    click.echo(f"Running command: {' '.join(command)}")

    # Start MongoDB
    mongodb = subprocess.Popen(["mongo-launch", "single"])

    # Execute the test command
    subprocess.run(command, stdin=None, stdout=None, stderr=None)

    # Terminate MongoDB
    mongodb.terminate()


cli.add_command(test)
