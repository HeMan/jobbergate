# views.py
from pathlib import Path
import importlib


from flask import render_template, Blueprint, Response, redirect, url_for
from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField,
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
)
from wtforms.validators import InputRequired, NumberRange


main_blueprint = Blueprint("main", __name__)


def _form_generator(application):

    importedlib = importlib.import_module(f"apps.{application}.views")

    class QuestioneryForm(FlaskForm):
        pass

    for field in importedlib.appform.questions:
        if field["type"] == "Text":
            setattr(
                QuestioneryForm,
                field["variablename"],
                StringField(
                    field["message"],
                    validators=[InputRequired()],
                    default=field["default"],
                ),
            )
        if field["type"] == "Integer":
            setattr(
                QuestioneryForm,
                field["variablename"],
                IntegerField(
                    field["message"],
                    default=field["default"],
                    validators=[
                        InputRequired(),
                        NumberRange(min=field["minval"], max=field["maxval"]),
                    ],
                ),
            )
        if field["type"] == "List":
            choices = []
            for choice in field["choices"]:
                if not isinstance(choice, tuple):
                    choices.append((str(choice), str(choice)))
                else:
                    choices.append((choice[1], choice[0]))
            setattr(
                QuestioneryForm,
                field["variablename"],
                SelectField(
                    field["message"], default=field["default"], choices=choices
                ),
            )

        if field["type"] in ["Directory", "File"]:
            setattr(
                QuestioneryForm,
                field["variablename"],
                StringField(field["message"], default=field["default"]),
            )

        if field["type"] == "Checkbox":
            choices = []
            for choice in field["choices"]:
                if not isinstance(choice, tuple):
                    choices.append((str(choice), str(choice)))
                else:
                    choices.append((choice[1], choice[0]))
            setattr(
                QuestioneryForm,
                field["variablename"],
                SelectMultipleField(
                    field["message"], default=field["default"], choices=choices
                ),
            )

        if field["type"] == "Confirm":
            setattr(
                QuestioneryForm,
                field["variablename"],
                BooleanField(field["message"], default=field["default"]),
            )
    QuestioneryForm.application = HiddenField(application)
    QuestioneryForm.submit = SubmitField()

    return QuestioneryForm()


@main_blueprint.route("/")
def home():
    return render_template("main/home.html")


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route("/apps/", methods=["GET", "POST"])
def apps():
    class AppForm(FlaskForm):
        application = SelectField("Select application")
        submit = SubmitField()

    appdir = Path("apps/")

    appform = AppForm()
    appform.application.choices = [
        (x.name, x.stem) for x in appdir.iterdir() if x.is_dir()
    ]

    if appform.validate_on_submit():
        # TODO: redirect direct to template selection if it has more then one
        # template
        return redirect(url_for("main.app", application=appform.data["application"]))

    return render_template("main/form.html", form=appform)


@main_blueprint.route("/app/<application>", methods=["GET", "POST"])
@main_blueprint.route("/app/<application>/<template>", methods=["GET", "POST"])
def app(application, template=None):
    questionsform = _form_generator(application)
    if not template:
        if len(list(Path(f"apps/{application}/templates/").glob("*.j2"))) > 1:
            return redirect(url_for("main.select_template", application=application))

        template = f"simple_slurm.j2"

    if questionsform.validate_on_submit():
        return Response(
            render_template(
                f"apps/{application}/templates/{template}", job=questionsform.data
            ),
            mimetype="text/x-shellscript",
            headers={"Content-Disposition": f"attachment;filename=jobfile.sh"},
        )

    return render_template(
        "main/form.html", form=questionsform, application=application, template=template
    )


@main_blueprint.route("/select_template/<application>", methods=["GET", "POST"])
def select_template(application):
    class TemplateForm(FlaskForm):
        template = SelectField("Choose template")
        application = HiddenField("application")
        submit = SubmitField()

    templateform = TemplateForm(application=application)

    templatedir = Path(f"apps/{application}/templates")
    templateform.template.choices = [
        (x.name, x.stem) for x in templatedir.iterdir() if x.is_file()
    ]

    if templateform.validate_on_submit():
        return redirect(
            url_for(
                "main.app",
                application=templateform.data["application"],
                template=templateform.data["template"],
            )
        )

    return render_template("main/form.html", form=templateform)
