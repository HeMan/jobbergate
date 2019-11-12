"""Creates dynamic CLI's for all apps"""
from collections import deque
from pathlib import Path
import click
import inquirer
import yaml
from flask import render_template_string
from flask.cli import with_appcontext

from jobbergate.lib import config, fullpath_import


def ask_questions(fields):
    """Asks the questions from all the fields"""
    questions = []

    while fields:
        field = fields.popleft()
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

            def validate(_, value):
                if minval is not None and maxval is not None:
                    return minval <= int(value) <= maxval
                if minval is not None:
                    return minval <= int(value)
                if maxval is not None:
                    return int(value) <= maxval
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
    """App factory. Looks in app directory and creates CLI for each of the
    directories"""

    def _callback(application):
        """Callback for the cli"""

        @with_appcontext
        def _wrapper(**kvargs):
            """The callback needs to be wrapped"""

            appview = fullpath_import(f"{application}", "views")

            data = {}

            # Check if the app has a controller file
            try:
                appcontroller = fullpath_import(f"{application}", "controller")

                prefuncs = appcontroller.workflow.prefuncs
                postfuncs = appcontroller.workflow.postfuncs
            except FileNotFoundError:
                prefuncs = {}
                postfuncs = {}

            outputfile = kvargs["output"]

            try:
                with open(
                    f"{config['apps']['path']}/{application}/config.yaml", "r"
                ) as ymlfile:
                    data.update(yaml.safe_load(ymlfile))
            except FileNotFoundError:
                pass

            # If the is a pre_-function in the controller, run that before all
            # questions
            if "" in prefuncs.keys():
                data.update(prefuncs[""](data) or {})

            # Ask the questions
            data.update(ask_questions(appview.appform.questions))

            # Check if workflows is defined
            if appview.appform.workflows:
                workflows = [
                    inquirer.List(
                        "workflow",
                        message="What workflow should be used",
                        choices=appview.appform.workflows.keys(),
                    )
                ]

                wfdata = inquirer.prompt(workflows)
                workflow = wfdata["workflow"]

                # If selected workflow have a pre_-function, run that now
                if workflow in prefuncs.keys():
                    data.update(prefuncs[workflow](data) or {})

                appview.appform.questions = deque()

                # "Instantiate" workflow questions
                wfquestions = appview.appform.workflows[workflow]
                wfquestions(data)

                # Ask workflow questions
                data.update(ask_questions(appview.appform.questions))

                # If selected workflow have a post_-function, run that now
                if workflow in postfuncs.keys():
                    data.update(postfuncs[workflow](data) or {})
                appview.appform.workflows = {}

            template = data.get("template", None) or data.get(
                "default_template", "job_template.j2"
            )
            templatefile = (
                kvargs["template"]
                or f"{config['apps']['path']}/{application}/templates/{template}"
            )

            # If there is a global post_-funtion, run that now
            if "" in postfuncs.keys():
                data.update(postfuncs[""](data) or {})
            with open(templatefile, "r") as template:
                return outputfile.write(
                    render_template_string(template.read(), job=data)
                )

        return _wrapper

    apps = [x.name for x in Path(config["apps"]["path"]).iterdir() if x.is_dir()]
    default_options = [
        click.Option(
            param_decls=("-t", "--template"),
            required=False,
            type=click.Path(exists=True),
        ),
        click.Argument(param_decls=["output"], type=click.File("w")),
    ]
    return [
        click.Command(name=app, callback=_callback(app), params=default_options)
        for app in apps
    ]


cmds = _app_factory()
