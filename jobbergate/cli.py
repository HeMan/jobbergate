"""
cli
===

Creates dynamic CLI's for all apps"""
from copy import deepcopy
from pathlib import Path
import json
import click
import inquirer
import yaml
from jinja2 import Environment, FileSystemLoader
from flask.cli import with_appcontext

from jobbergate.lib import jobbergateconfig, fullpath_import
from jobbergate import appform


def flatten(deeplist):
    """Helper function to flatten lists and tuples.

    :param list deeplist: list of varying dept
    :returns: flattened list
    :rtype: list
    """
    out = []
    for item in deeplist:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def parse_field(field, ignore=None):
    """Parses the question field and returns a list of inquirer questions.

    :param jobbergate.appform.QuestionBase field: The question to parse
    :param ignore: function to decide if the question should be ignored/hidden
    :returns: inquirer question
    :rtype: inquirer.Question
    """
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

    if isinstance(field, appform.Const):
        return inquirer.Text(
            field.variablename, message="", default=field.default, ignore=True,
        )


def ask_questions(fields, answerfile, use_defaults=False):
    """Asks the questions from all the fields.

    :param list[jobbergate.appform.QuestionBase] fields: List with questions
    :param dict answerfile: dict with prepopulated answers
    :param bool use_defaults: option to use default value instead of asking, when possible
    :returns: all answers
    :rtype: dict
    """
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
        elif use_defaults and question.default is not None:
            retval.update({question.name: question.default})
            print(f"Default used: {question.name}={question.default}")
        else:
            questionstoask.append(question)
    try:
        retval.update(inquirer.prompt(questionstoask))
    except TypeError:
        exit(0)

    return retval


def parse_prefill(arguments):
    """Parses ``-p/--prefill`` command line arguments.

    :param list[string] arguments: all arguments given to -p/--prefill
    :returns: dict with all command line answers
    :rtype: dict
    """
    retval = {}
    for arg in arguments:
        key, value = arg.split("=")
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        else:
            # Save as number if possible
            try:
                original = value
                value = float(original)
                value = int(original)
            except ValueError:
                pass
        retval.update({key: value})
    return retval


def app_factory():
    """
    This is the workhorse of cli module.

    Click needs to have the code as a callback so we need to create the
    _callback function, which in turn returns a wrapper for each application.
    The app factory loops throug all the applications in the configed
    directory, and creates callbacks for each of them. This is the real
    workhorse in cli."""

    def _callback(application):
        """Callback for the cli"""

        @with_appcontext
        def _wrapper(**kvargs):
            """The callback needs to be wrapped"""

            appview = fullpath_import(f"{application}", "views")

            data = {}
            data["jobbergateconfig"] = deepcopy(jobbergateconfig)
            saveanswers = kvargs["saveanswers"]
            if kvargs["answerfile"]:
                with open(kvargs["answerfile"]) as jsonfile:
                    answerfile = json.load(jsonfile)
            else:
                answerfile = {}

            # Update data from answerfile with command line arguments
            answerfile.update(parse_prefill(kvargs["prefill"]))
            # Check if the app has a controller file
            try:
                appcontroller = fullpath_import(f"{application}", "controller")

                prefuncs = appcontroller.workflow.prefuncs
                postfuncs = appcontroller.workflow.postfuncs
            except ModuleNotFoundError:
                prefuncs = {}
                postfuncs = {}

            outputfile = kvargs["output"]
            use_defaults = kvargs["fast"]

            try:
                with open(
                    f"{jobbergateconfig['apps']['path']}/{application}/config.yaml", "r"
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
            answers = ask_questions(questions, answerfile, use_defaults)
            if saveanswers:
                savedanswers = answers

            data.update(answers)

            if "mainflow" in postfuncs.keys():
                data.update(postfuncs["mainflow"](data) or {})

            if "nextworkflow" in data or (
                "flows" in answerfile and "mainflow" in answerfile["flows"]
            ):
                if saveanswers:
                    savedanswers["flow"] = {}
                currentworkflow = "mainflow"
                while True:
                    if "flows" in answerfile:
                        workflow = answerfile["flows"].get(currentworkflow) or data.pop(
                            "nextworkflow"
                        )
                        if workflow in answerfile["flows"]:
                            answerfile["nextworkflow"] = answerfile["flows"][workflow]
                    else:
                        workflow = data.pop("nextworkflow")
                    if saveanswers:
                        savedanswers["flow"].update({currentworkflow: workflow})
                    currentworkflow = workflow
                    # If nextworkflow isn't defined, raise exception
                    if workflow not in appview.__dict__:
                        raise NameError(f"Couldn't find workflow {workflow}")

                    # If selected workflow have a pre_-function, run that now
                    if workflow in prefuncs.keys():
                        data.update(prefuncs[workflow](data) or {})

                    # "Instantiate" workflow questions
                    wfquestions = appview.__dict__[workflow]
                    questions = wfquestions(data)
                    answers = ask_questions(questions, answerfile, use_defaults)
                    if saveanswers:
                        savedanswers.update(answers)
                    data.update(answers)

                    # If selected workflow have a post_-function, run that now
                    if workflow in postfuncs.keys():
                        data.update(postfuncs[workflow](data) or {})

                    if "nextworkflow" not in data:
                        break

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

                    try:
                        wfdata = inquirer.prompt(workflows)
                    except TypeError:
                        exit(0)
                    if "mainflow" in postfuncs.keys():
                        data.update(postfuncs["mainflow"](data) or {})
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
                answers = ask_questions(questions, answerfile, use_defaults)
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
                templatedir = (
                    f"{jobbergateconfig['apps']['path']}/{application}/templates/"
                )
                template = data.get("template", None) or data.get(
                    "default_template", "job_template.j2"
                )

            # If there is a global post_-function, run that now
            if "" in postfuncs.keys():
                data.update(postfuncs[""](data) or {})

            if saveanswers:
                with open(kvargs["saveanswers"], "w") as jsonfile:
                    json.dump(savedanswers, jsonfile, indent=4)

            jinjaenv = Environment(loader=FileSystemLoader(templatedir))
            jinjatemplate = jinjaenv.get_template(template)
            return outputfile.write(jinjatemplate.render(data=data))

        return _wrapper

    if not Path(jobbergateconfig["apps"]["path"]).is_dir():
        return []

    apps = [
        x.name for x in Path(jobbergateconfig["apps"]["path"]).iterdir() if x.is_dir()
    ]
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
            help="Creates a pre-populated answer file",
            required=False,
            type=click.Path(),
        ),
        click.Option(
            param_decls=("-f", "--fast"),
            help="Fast-forward by using defaults instead of asking when possible.",
            required=False,
            is_flag=True,
        ),
        click.Argument(param_decls=["output"], type=click.File("w")),
    ]
    readmefirstline = {}
    params = {}
    for app in apps:
        try:
            with open(f"{jobbergateconfig['apps']['path']}/{app}/README") as readmefile:
                readmefirstline[app] = readmefile.readline()
        except FileNotFoundError:
            readmefirstline[app] = ""

        try:
            with open(
                f"{jobbergateconfig['apps']['path']}/{app}/parameters"
            ) as paramsfile:
                params[app] = paramsfile.read()
        except FileNotFoundError:
            params[app] = ""

    return [
        click.Command(
            name=app,
            help=readmefirstline[app],
            callback=_callback(app),
            params=default_options
            + [
                click.Option(
                    param_decls=("-p", "--prefill"),
                    help=params[app] or "Prefill answers",
                    required=False,
                    multiple=True,
                    type=click.STRING,
                )
            ],
        )
        for app in apps
    ]


try:
    cmds = app_factory()
except KeyError:
    pass
