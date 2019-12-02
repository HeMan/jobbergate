"""Creates dynamic CLI's for all apps"""
from pathlib import Path
import json
import click
import inquirer
import yaml
from jinja2 import Environment, FileSystemLoader
from flask.cli import with_appcontext

from jobbergate.lib import config, fullpath_import
from jobbergate import appform


def flatten(deeplist):
    """Helper function to flatten lists and tuples"""
    out = []
    for item in deeplist:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def parse_field(field, ignore=None):
    """Parses the question field and returns a list of inquirer questions"""
    if isinstance(field, appform.Text):
        return inquirer.Text(
            field.variablename,
            message=field.message,
            default=field.default,
            ignore=ignore,
        )

    if isinstance(field, appform.Integer):
        return inquirer.Text(
            field.variablename,
            message=field.message,
            default=field.default,
            validate=field.validate,
            ignore=ignore,
        )

    if isinstance(field, appform.List):
        return inquirer.List(
            field.variablename,
            message=field.message,
            choices=field.choices,
            default=field.default,
            ignore=ignore,
        )

    if isinstance(field, appform.Directory):
        return inquirer.Path(
            field.variablename,
            message=field.message,
            path_type=inquirer.Path.DIRECTORY,
            default=field.default,
            exists=field.exists,
            ignore=ignore,
        )

    if isinstance(field, appform.File):
        return inquirer.Path(
            field.variablename,
            message=field.message,
            path_type=inquirer.Path.FILE,
            default=field.default,
            exists=field.exists,
            ignore=ignore,
        )

    if isinstance(field, appform.Checkbox):
        return inquirer.Checkbox(
            field.variablename,
            message=field.message,
            choices=field.choices,
            default=field.default,
            ignore=ignore,
        )

    if isinstance(field, appform.Confirm):
        return inquirer.Confirm(
            field.variablename,
            message=field.message,
            default=field.default,
            ignore=ignore,
        )

    if isinstance(field, appform.BooleanList):
        retval = [
            inquirer.Confirm(
                field.variablename,
                message=field.message,
                default=field.default,
                ignore=ignore,
            )
        ]

        if field.whenfalse:
            retval.extend(
                [parse_field(wf, ignore=field.ignore) for wf in field.whenfalse]
            )
        if field.whentrue:
            retval.extend(
                [parse_field(wt, ignore=field.noignore) for wt in field.whentrue]
            )

        return retval


def ask_questions(fields, answerfile):
    """Asks the questions from all the fields"""
    questions = []
    questionstoask = []
    retval = {}

    while fields:
        field = fields.pop(0)
        question = parse_field(field)
        questions.append(question)

    # Check if questions has already been answered
    for question in flatten(questions):
        if question.name in answerfile:
            retval.update({question.name: answerfile[question.name]})
        else:
            questionstoask.append(question)

    retval.update(inquirer.prompt(questionstoask))

    return retval


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
            saveanswers = kvargs["saveanswers"]
            if kvargs["answerfile"]:
                with open(kvargs["answerfile"]) as jsonfile:
                    answerfile = json.load(jsonfile)
            else:
                answerfile = {}
            # Check if the app has a controller file
            try:
                appcontroller = fullpath_import(f"{application}", "controller")

                prefuncs = appcontroller.workflow.prefuncs
                postfuncs = appcontroller.workflow.postfuncs
            except ModuleNotFoundError:
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
            questions = appview.mainflow(data)
            answers = ask_questions(questions, answerfile)
            if saveanswers:
                savedanswers = answers

            data.update(answers)
            # Check if workflows is defined
            if appview.appform.workflows:
                if "workflow" in answerfile:
                    workflow = answerfile["workflow"]
                else:
                    workflows = [
                        inquirer.List(
                            "workflow",
                            message="What workflow should be used",
                            choices=appview.appform.workflows.keys(),
                        )
                    ]

                    wfdata = inquirer.prompt(workflows)
                    workflow = wfdata["workflow"]

                if saveanswers:
                    savedanswers.update({"workflow": workflow})

                # If selected workflow have a pre_-function, run that now
                if workflow in prefuncs.keys():
                    data.update(prefuncs[workflow](data) or {})

                # "Instantiate" workflow questions
                wfquestions = appview.appform.workflows[workflow]
                questions = wfquestions(data)

                # Ask workflow questions
                answers = ask_questions(questions, answerfile)
                if saveanswers:
                    savedanswers.update(answers)
                data.update(answers)

                # If selected workflow have a post_-function, run that now
                if workflow in postfuncs.keys():
                    data.update(postfuncs[workflow](data) or {})
                appview.appform.workflows = {}

            if kvargs["template"]:
                templatedir = str(Path(kvargs["template"]).parent)
                template = Path(kvargs["template"]).name
            else:
                templatedir = f"{config['apps']['path']}/{application}/templates/"
                template = data.get("template", None) or data.get(
                    "default_template", "job_template.j2"
                )

            # If there is a global post_-funtion, run that now
            if "" in postfuncs.keys():
                data.update(postfuncs[""](data) or {})

            if saveanswers:
                with open(kvargs["saveanswers"], "w") as jsonfile:
                    json.dump(savedanswers, jsonfile)

            jinjaenv = Environment(loader=FileSystemLoader(templatedir))
            jinjatemplate = jinjaenv.get_template(template)
            return outputfile.write(jinjatemplate.render(job=data))

        return _wrapper

    if not Path(config["apps"]["path"]).is_dir():
        return []

    apps = [x.name for x in Path(config["apps"]["path"]).iterdir() if x.is_dir()]
    default_options = [
        click.Option(
            param_decls=("-t", "--template"),
            help="Full path to template file",
            required=False,
            type=click.Path(exists=True),
        ),
        click.Option(
            param_decls=("-a", "--answerfile"),
            help="Full path to pre-populate answer file.",
            required=False,
            type=click.Path(exists=True),
        ),
        click.Option(
            param_decls=("-s", "--saveanswers"),
            help="Creates a pre-poulated answer file",
            required=False,
            type=click.Path(),
        ),
        click.Argument(param_decls=["output"], type=click.File("w")),
    ]
    readme = {}
    for app in apps:
        try:
            with open(f"{config['apps']['path']}/{app}/README") as f:
                readme[app] = f.read()
        except FileNotFoundError:
            readme[app] = ""

    return [
        click.Command(
            name=app, help=readme[app], callback=_callback(app), params=default_options
        )
        for app in apps
    ]


cmds = _app_factory()
