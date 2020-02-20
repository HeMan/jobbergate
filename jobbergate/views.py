"""
views
=====

The web part of jobbergate.
"""
import sys
from copy import deepcopy
from pathlib import Path
from collections import deque
from jinja2 import Environment, FileSystemLoader
import yaml


from flask import (
    Blueprint,
    Response,
    current_app,
    json,
    redirect,
    render_template,
    session,
    url_for,
    request,
)
from flask_login import login_user, logout_user, login_required
from flask_ldap3_login.forms import LDAPLoginForm
from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField,
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    FormField,
)
from wtforms.validators import InputRequired, NumberRange

from jobbergate.lib import jobbergateconfig, fullpath_import
from jobbergate import appform
from jobbergate.models import User

from jobbergate import users

main_blueprint = Blueprint("main", __name__, template_folder="templates")


def parse_field(form, field, render_kw=None):
    """Parses the question field and populates a FlaskForm with the fields.

    :param FlaskForm form: The form to populate
    :param jobbergate.appform.QuestionBase field: The question to parse
    :param render_kw: extra attributes for the field
    :returns: Form with all the fields
    :rtype: FlaskForm
    """
    if isinstance(field, appform.Text):
        setattr(
            form,
            field.variablename,
            StringField(
                field.message,
                validators=[InputRequired()],
                default=field.default,
                render_kw=render_kw,
            ),
        )
    if isinstance(field, appform.Integer):
        setattr(
            form,
            field.variablename,
            IntegerField(
                field.message,
                default=field.default,
                validators=[
                    InputRequired(),
                    NumberRange(min=field.minval, max=field.maxval),
                ],
                render_kw=render_kw,
            ),
        )
    if isinstance(field, appform.List):
        choices = []
        for choice in field.choices:
            if not isinstance(choice, tuple):
                choices.append((str(choice), str(choice)))
            else:
                choices.append((choice[1], choice[0]))
        setattr(
            form,
            field.variablename,
            SelectField(
                field.message,
                default=field.default,
                choices=choices,
                render_kw=render_kw,
            ),
        )

    if isinstance(field, (appform.Directory, appform.File)):
        setattr(
            form,
            field.variablename,
            StringField(field.message, default=field.default, render_kw=render_kw),
        )

    if isinstance(field, appform.Checkbox):
        choices = []
        for choice in field.choices:
            if not isinstance(choice, tuple):
                choices.append((str(choice), str(choice)))
            else:
                choices.append((choice[1], choice[0]))
        setattr(
            form,
            field.variablename,
            SelectMultipleField(
                field.message,
                default=field.default,
                choices=choices,
                render_kw=render_kw,
            ),
        )

    if isinstance(field, appform.Confirm):
        setattr(
            form,
            field.variablename,
            BooleanField(field.message, default=field.default, render_kw=render_kw),
        )

    if isinstance(field, appform.BooleanList):
        fieldid = 0

        class FalseForm(FlaskForm):
            pass

        class TrueForm(FlaskForm):
            pass

        if field.whenfalse:
            for wf in field.whenfalse:
                FalseForm = parse_field(
                    FalseForm,
                    wf,
                    render_kw={"id": f"{field.variablename}_false_{fieldid}"},
                )
                fieldid += 1
        if field.whentrue:
            for wt in field.whentrue:
                TrueForm = parse_field(
                    TrueForm,
                    wt,
                    render_kw={"id": f"{field.variablename}_true_{fieldid}"},
                )
                fieldid += 1
        setattr(
            form,
            field.variablename,
            BooleanField(
                field.message,
                default=field.default,
                render_kw={"onchange": "toggle_questions(this);"},
            ),
        )
        setattr(form, f"{field.variablename}_trueform", FormField(TrueForm, label=""))
        setattr(form, f"{field.variablename}_falseform", FormField(FalseForm, label=""))

    if isinstance(field, appform.Const):
        setattr(
            form,
            field.variablename,
            HiddenField(field.variablename, default=field.default),
        )

    return form


def form_generator(application_name, templates, workflow):
    """Generates form from workflow function

    :param string application_name: Name of the application
    :param list[string] templates: List of availabe templates
    :param workflow: workflow function
    :returns: A populated QuestionaryForm
    :rtype: FlaskForm
    """
    if "data" in session:
        data = json.loads(session["data"])
    else:
        data = {}

    class QuestioneryForm(FlaskForm):
        pass

    if len(templates) == 1:
        QuestioneryForm.template = HiddenField(default=templates[0][0])
    elif len(templates) > 1:
        if "default_template" in data:
            default_template = data["default_template"]
        else:
            default_template = None
        QuestioneryForm.template = SelectField(
            "Select template", choices=templates, default=default_template
        )
    questions = workflow(data)
    while questions:
        field = questions.pop(0)
        QuestioneryForm = parse_field(QuestioneryForm, field)

    if appform.workflows:
        choices = [(None, "--- Select ---")]
        choices.extend([(k, k) for k in appform.workflows.keys()])
        QuestioneryForm.workflow = SelectField("Select workflow", choices=choices)
        appform.workflows = {}

    QuestioneryForm.application = HiddenField("application", default=application_name)
    QuestioneryForm.submit = SubmitField()

    return QuestioneryForm()


@main_blueprint.route("/")
def home():
    """route for /

    Clears out session data and renders home.html template"""
    if "data" in session:
        del session["data"]
    if "templates" in session:
        del session["templates"]
    if "LDAP_HOST" not in current_app.config:
        user = User("temp", "temp", "temp")
        login_user(user)
        users["temp"] = user
    return render_template("main/home.html")


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route("/apps/", methods=["GET", "POST"])
@login_required
def applications():
    """route for /apps/

    Lets users select from available applications"""

    class AppForm(FlaskForm):
        application = SelectField("Select application")
        submit = SubmitField()

    appdir = Path(jobbergateconfig["apps"]["path"])

    appwebform = AppForm()
    appwebform.application.choices = [
        (x.name, x.stem) for x in appdir.iterdir() if x.is_dir()
    ]

    if appwebform.validate_on_submit():
        application_name = appwebform.data["application"]
        templatedir = Path(
            f"{jobbergateconfig['apps']['path']}/{application_name}/templates/"
        )
        session["templates"] = json.dumps(
            [template.name for template in templatedir.glob("*.j2")]
        )
        return redirect(url_for("main.application", application_name=application_name))

    return render_template("main/form.html", form=appwebform)


@main_blueprint.route("/app/<application_name>", methods=["GET", "POST"])
@login_required
def application(application_name):
    """route for /app/<application_name>

    :param application_name: Name of application

    Renders base questions for <application_name> and lets users answer them."""

    templates = [(template, template) for template in json.loads(session["templates"])]
    importedlib = fullpath_import(application_name, "views")

    data = {}
    data["jobbergateconfig"] = deepcopy(jobbergateconfig)
    try:
        with open(
            f"{jobbergateconfig['apps']['path']}/{application_name}/config.yaml", "r"
        ) as ymlfile:
            data.update(yaml.safe_load(ymlfile))
    except FileNotFoundError:
        pass

    try:
        appcontroller = fullpath_import(f"{application_name}", "controller")

        prefuncs = appcontroller.workflow.prefuncs
        postfuncs = appcontroller.workflow.postfuncs
    except ModuleNotFoundError:
        prefuncs = {}
        postfuncs = {}
    if request.method == "GET":
        # If the is a pre_-function in the controller, run that before all
        # questions
        if "" in prefuncs.keys():
            data.update(prefuncs[""](data) or {})

    questionsform = form_generator(application_name, templates, importedlib.mainflow)

    if questionsform.validate_on_submit():
        data.update(json.loads(session["data"]))
        data.update(questionsform.data)
        session["data"] = json.dumps(data)
        if "mainflow" in postfuncs:
            data.update(postfuncs["mainflow"](data) or {})

        if "workflow" or "nextworkflow" in questionsform:
            workflow = questionsform.data.get("workflow") or questionsform.data.get(
                "nextworkflow"
            )
            if "views" in sys.modules:
                del sys.modules["views"]
            return redirect(
                url_for(
                    "main.renderworkflow",
                    application_name=application_name,
                    workflow=workflow,
                )
            )
        templatedir = (
            f"{jobbergateconfig['apps']['path']}/{application_name}/templates/"
        )
        template = data.get("template", None) or data.get(
            "default_template", "job_template.j2"
        )
        jinjaenv = Environment(loader=FileSystemLoader(templatedir))
        jinjatemplate = jinjaenv.get_template(template)
        return Response(
            jinjatemplate.render(data=data),
            mimetype="text/x-shellscript",
            headers={"Content-Disposition": f"attachment;filename=jobfile.sh"},
        )

    session["data"] = json.dumps(data)
    if "views" in sys.modules:
        del sys.modules["views"]
    return render_template(
        "main/form.html", form=questionsform, application_name=application_name,
    )


@main_blueprint.route(
    "/workflow/<application_name>/<workflow>", methods=["GET", "POST"]
)
@login_required
def renderworkflow(application_name, workflow):
    """route for /workflow/<application_name>/<workflow>

    :param application_name: application name
    :param workflow: workflow name

    Renders <workflow> for <application_name> and lets user answer questions."""

    appview = fullpath_import(f"{application_name}", "views")
    data = json.loads(session["data"])
    try:
        appcontroller = fullpath_import(f"{application_name}", "controller")

        prefuncs = appcontroller.workflow.prefuncs
        postfuncs = appcontroller.workflow.postfuncs
    except ModuleNotFoundError:
        prefuncs = {}
        postfuncs = {}

    if workflow in prefuncs.keys():
        data.update(prefuncs[workflow](data) or {})

    appview.appform.questions = deque()
    if workflow in appview.appform.workflows:
        wfquestions = appview.appform.workflows[workflow]
    else:
        if workflow not in appview.__dict__:
            raise NameError(f"Couldn't find workflow {workflow}")

        wfquestions = appview.__dict__[workflow]

    # "Instantiate" workflow questions
    wfquestions(data)

    # Ask workflow questions
    appview.appform.workflows = {}
    questionsform = form_generator(application_name, [], wfquestions)

    if questionsform.validate_on_submit():
        data.update(json.loads(session["data"]))
        data.update(questionsform.data)
        session["data"] = json.dumps(data)
        # If selected workflow have a post_-function, run that now
        if workflow in postfuncs.keys():
            data.update(postfuncs[workflow](data) or {})
        if ("workflow" or "nextworkflow" in questionsform) or ("nextworkflow" in data):
            workflow = (
                questionsform.data.get("workflow")
                or questionsform.data.get("nextworkflow")
                or data["nextworkflow"]
            )
            if workflow:
                return redirect(
                    url_for(
                        "main.renderworkflow",
                        application_name=application_name,
                        workflow=workflow,
                    )
                )
        # FIXME: Same as in apps function.
        # DRY
        templatedir = (
            f"{jobbergateconfig['apps']['path']}/{application_name}/templates/"
        )
        template = data.get("template", None) or data.get(
            "default_template", "job_template.j2"
        )
        jinjaenv = Environment(loader=FileSystemLoader(templatedir))
        jinjatemplate = jinjaenv.get_template(template)
        return Response(
            jinjatemplate.render(data=data),
            mimetype="text/x-shellscript",
            headers={"Content-Disposition": f"attachment;filename=jobfile.sh"},
        )

    return render_template(
        "main/form.html", form=questionsform, application_name=application_name,
    )


@main_blueprint.route("/login/", methods=["GET", "POST"])
def login():
    loginform = LDAPLoginForm()
    if loginform.validate_on_submit():
        login_user(loginform.user)
        next_url = request.args.get("next")
        return redirect(next_url or url_for("main.home"))
    return render_template("main/form.html", form=loginform)


@main_blueprint.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("main.home"))
