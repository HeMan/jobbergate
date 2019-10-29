"""Creates dynamic CLI's for all apps"""
import importlib
from pathlib import Path
import click
import inquirer
from flask import render_template
from flask.cli import with_appcontext


def ask_questions(fields):
    """Asks the questions from all the fields"""
    questions = []

    for field in fields:
        if field["type"] == "Text":
            questions.append(
                inquirer.Text(
                    field["variablename"],
                    message=field["message"],
                    default=field["default"],
                )
            )

        if field["type"] == "Integer":
            minval = field["minval"]
            maxval = field["maxval"]

            def validate(_, x):
                if minval is not None and maxval is not None:
                    return minval <= int(x) <= maxval
                if minval is not None:
                    return minval <= int(x)
                if maxval is not None:
                    return int(x) <= maxval
                return True

            questions.append(
                inquirer.Text(
                    field["variablename"],
                    message=field["message"],
                    default=field["default"],
                    validate=validate,
                )
            )

        if field["type"] == "List":
            questions.append(
                inquirer.List(
                    field["variablename"],
                    message=field["message"],
                    choices=field["choices"],
                    default=field["default"],
                )
            )

        if field["type"] == "Directory":
            questions.append(
                inquirer.Path(
                    field["variablename"],
                    message=field["message"],
                    path_type=inquirer.Path.DIRECTORY,
                    default=field["default"],
                    exists=field["exists"],
                )
            )

        if field["type"] == "File":
            questions.append(
                inquirer.Path(
                    field["variablename"],
                    message=field["message"],
                    path_type=inquirer.Path.FILE,
                    default=field["default"],
                    exists=field["exists"],
                )
            )

        if field["type"] == "Checkbox":
            questions.append(
                inquirer.Checkbox(
                    field["variablename"],
                    message=field["message"],
                    choices=field["choices"],
                    default=field["default"],
                )
            )

        if field["type"] == "Confirm":
            questions.append(
                inquirer.Confirm(
                    field["variablename"],
                    message=field["message"],
                    default=field["default"],
                )
            )
    return inquirer.prompt(questions)


def _app_factory():
    def _callback(application):
        @with_appcontext
        def _callbackier(**kvargs):
            importedlib = importlib.import_module(f"apps.{application}.views")

            outputfile = kvargs["output"]
            templatefile = (
                kvargs["template"] or f"apps/{application}/templates/simple_slurm.j2"
            )
            data = ask_questions(importedlib.appform.questions)

            if importedlib.appform.workflows:
                workflows = [
                    inquirer.List(
                        "workflow",
                        message="What workflow should be used",
                        choices=importedlib.appform.workflows,
                    )
                ]
                wfdata = inquirer.prompt(workflows)

                importedlib.appform.questions = []
                wfquestions = wfdata["workflow"]
                wfquestions()
                data.update(ask_questions(importedlib.appform.questions))

            return outputfile.write(render_template(templatefile, job=data))

        return _callbackier

    appdir = Path("apps/")
    default_options = [
        click.Option(
            param_decls=("-t", "--template"),
            required=False,
            type=click.Path(exists=True),
        ),
        click.Argument(param_decls=["output"], type=click.File("w")),
    ]
    return [
        click.Command(name=x.name, callback=_callback(x.name), params=default_options)
        for x in appdir.iterdir()
        if x.is_dir()
    ]


cmds = _app_factory()
