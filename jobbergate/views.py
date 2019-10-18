# views.py
from pathlib import Path
import importlib


from flask import render_template, Blueprint, Response
from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField,
    FileField,
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

    QuestioneryForm.submit = SubmitField()

    return QuestioneryForm()


@main_blueprint.route("/")
def home():
    return render_template("main/home.html")


@main_blueprint.route("/about/")
def about():
    return render_template("main/about.html")


@main_blueprint.route("/apps/")
def apps():
    appdir = Path("apps/")
    applications = [x.name for x in appdir.iterdir() if x.is_dir()]
    return render_template("main/apps.html", applications=applications)


@main_blueprint.route("/app/<application>", methods=["GET", "POST"])
def app(application):
    questionsform = _form_generator(application)
    if questionsform.validate_on_submit():
        return Response(
            render_template(
                f"apps/{application}/templates/simple_slurm.j2", job=questionsform.data
            ),
            mimetype="text/x-shellscript",
        )

    return render_template(
        "main/questions.html", form=questionsform, application=application
    )
