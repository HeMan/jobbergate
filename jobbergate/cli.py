import importlib
from pathlib import Path
import click
import inquirer
from flask import render_template
from flask.cli import with_appcontext


def _app_factory():
    def _callback(application):
        @with_appcontext
        def _callbackier():
            importedlib = importlib.import_module(f"apps.{application}.views")

            questions = []

            for field in importedlib.appform.questions:
                if field["type"] == "Text":
                    questions.append(
                        inquirer.Text(
                            field["variablename"],
                            message=field["message"],
                            default=field["default"],
                        )
                    )

                if field["type"] == "Integer":
                    # FIXME: validating doesn't work when called without limits
                    questions.append(
                        inquirer.Text(
                            field["variablename"],
                            message=field["message"],
                            default=field["default"],
                            # validate=lambda _, x: field["minval"]
                            # <= int(x)
                            # <= field["maxval"],
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
