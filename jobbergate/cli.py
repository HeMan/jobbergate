import click
from pathlib import Path
import inquirer
import importlib
from flask import render_template
from flask.cli import with_appcontext


def _app_factory():
    def _callback(application):
        @with_appcontext
        def _callbackier(*args, **kvargs):
            importedlib = importlib.import_module(f"apps.{application}.views")

            questions = []

            for field in importedlib.appform.questions:
                questions.append(
                    inquirer.Text(field["variablename"], message=field["question"])
                )

            data = inquirer.prompt(questions)

            print(
                render_template(
                    f"apps/{application}/templates/simple_slurm.j2", job=data
                )
            ),

        return _callbackier

    appdir = Path("apps/")
    return [
        click.Command(name=x.name, callback=_callback(x.name))
        for x in appdir.iterdir()
        if x.is_dir()
    ]


cmds = _app_factory()
