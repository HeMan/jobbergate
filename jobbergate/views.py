# views.py
from pathlib import Path


from flask import render_template, Blueprint, Response
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired


main_blueprint = Blueprint("main", __name__)


def _form_generator(application):
    import importlib

    importedlib = importlib.import_module(f"apps.{application}.views")

    class QuestioneryForm(FlaskForm):
        pass

    for field in importedlib.appform.questions:
        setattr(
            QuestioneryForm,
            field["variablename"],
            StringField(field["question"], validators=[InputRequired()]),
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
