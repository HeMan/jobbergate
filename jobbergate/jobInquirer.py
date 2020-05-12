"""
JobInquirer
===
as the inquirer package, adapted for the jobbergate. Includes classes for different question types, and QuestionBase
"""

import inquirer


class QuestionBase:
    """Baseclass for questions.
    All questions have variablename, message and an optional default.

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    """

    def __init__(self, variablename, message, default):
        self.variablename = variablename
        self.message = message
        self.default = default

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        raise Exception("Inheriting class must be overwrite this.")

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object."""
        raise Exception("Inheriting class must be overwrite this.")


class Text(QuestionBase):
    """Asks for a text value.

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    """

    def __init__(self, variablename, message, default=None):
        super().__init__(variablename, message, default)

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Text(
            self.variablename,
            message=self.message,
            default=self.default,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            StringField(
                self.message,
                validators=[InputRequired()],
                default=self.default,
                render_kw=render_kw,
            ),
        )
        return form


class Integer(QuestionBase):
    """Asks for an integer value. Could have min and/or max constrains.

    :param variablename: The variable name to set
    :param message: Message to show
    :param minval: Minumum value
    :param maxval: Maximum value
    :param default: Default value
    """

    def __init__(self, variablename, message, minval=None, maxval=None, default=None):
        super().__init__(variablename, message, default)
        self.maxval = maxval
        self.minval = minval

    def validate(self, _, value):
        if self.minval is not None and self.maxval is not None:
            return self.minval <= int(value) <= self.maxval
        if self.minval is not None:
            return self.minval <= int(value)
        if self.maxval is not None:
            return int(value) <= self.maxval
        return True

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Text(
            self.variablename,
            message=self.message,
            default=self.default,
            validate=self.validate,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            IntegerField(
                self.message,
                default=self.default,
                validators=[
                    InputRequired(),
                    NumberRange(min=self.minval, max=self.maxval),
                ],
                render_kw=render_kw,
            ),
        )
        return form

class List(QuestionBase):
    """Gives the user a list to choose one from.

    :param variablename: The variable name to set
    :param message: Message to show
    :param choices: List with choices
    :param default: Default value"""

    def __init__(self, variablename, message, choices, default=None):
        super().__init__(variablename, message, default)
        self.choices = choices

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.List(
            self.variablename,
            message=self.message,
            choices=self.choices,
            default=self.default,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        choices = []
        for choice in self.choices:
            if not isinstance(choice, tuple):
                choices.append((str(choice), str(choice)))
            else:
                choices.append((choice[1], choice[0]))
        setattr(
            form,
            self.variablename,
            SelectField(
                self.message,
                default=self.default,
                choices=choices,
                render_kw=render_kw,
            ),
        )
        return form


class Directory(QuestionBase):
    """Asks for a directory name. If `exists` is `True` it checks if path exists and is a directory.

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    :param exists: Checks if given directory exists"""

    def __init__(self, variablename, message, default=None, exists=None):
        super().__init__(variablename, message, default)
        self.exists = exists

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Path(
            self.variablename,
            message=self.message,
            path_type=inquirer.Path.DIRECTORY,
            default=self.default,
            exists=self.exists,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            StringField(self.message, default=self.default, render_kw=render_kw),
        )
        return form


class File(QuestionBase):
    """Asks for a file name. If `exists` is `True` it checks if path exists and is a directory.

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    :param exists: Checks if given file exists"""

    def __init__(self, variablename, message, default=None, exists=None):
        super().__init__(variablename, message, default)
        self.exists = exists

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Path(
            self.variablename,
            message=self.message,
            path_type=inquirer.Path.FILE,
            default=self.default,
            exists=self.exists,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            StringField(self.message, default=self.default, render_kw=render_kw),
        )
        return form


class Checkbox(QuestionBase):
    """Gives the user a list to choose multiple entries from.

    :param variablename: The variable name to set
    :param message: Message to show
    :param choices: List with choices
    :param default: Default value(s)"""

    def __init__(self, variablename, message, choices, default=None):
        super().__init__(variablename, message, default)
        self.choices = choices

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Checkbox(
            self.variablename,
            message=self.message,
            choices=self.choices,
            default=self.default,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        choices = []
        for choice in self.choices:
            if not isinstance(choice, tuple):
                choices.append((str(choice), str(choice)))
            else:
                choices.append((choice[1], choice[0]))
        setattr(
            form,
            self.variablename,
            SelectMultipleField(
                self.message,
                default=self.default,
                choices=choices,
                render_kw=render_kw,
            ),
        )
        return form


class Confirm(QuestionBase):
    """Asks a question with an boolean answer (true/false).

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    """

    def __init__(self, variablename, message, default=None):
        super().__init__(variablename, message, default)

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Confirm(
            self.variablename,
            message=self.message,
            default=self.default,
            ignore=ignore,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            BooleanField(self.message, default=self.default, render_kw=render_kw),
        )
        return form


class BooleanList(QuestionBase):
    """Gives the use a boolean question, and depending on answer it shows `whentrue` or `whenfalse` questions.
    `whentrue` and `whenfalse` are lists with questions. Could contain multiple levels of BooleanLists.


    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Default value
    :param whentrue: List of questions to show if user answers yes/true on this question
    :param whentrue: List of questions to show if user answers no/false on this question
    """

    def __init__(
        self, variablename, message, default=None, whentrue=None, whenfalse=None
    ):
        super().__init__(variablename, message, default)
        if whentrue is None and whenfalse is None:
            raise ValueError("Empty questions lists")
        self.whentrue = whentrue
        self.whenfalse = whenfalse
        self.ignore = lambda a: a[self.variablename]
        self.noignore = lambda a: not a[self.variablename]

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        retval = [
            inquirer.Confirm(
                self.variablename,
                message=self.message,
                default=self.default,
                ignore=ignore,
            )
        ]

        if self.whenfalse:
            retval.extend(
                [wf.toInquirerQuestion(ignore=self.ignore) for wf in self.whenfalse]
            )
        if self.whentrue:
            retval.extend(
                [wt.toInquirerQuestion(ignore=self.noignore) for wt in self.whentrue]
            )

        return retval

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        fieldid = 0

        class FalseForm(FlaskForm):
            pass

        class TrueForm(FlaskForm):
            pass

        if self.whenfalse:
            for wf in self.whenfalse:
                FalseForm = wf.populateFlaskForm(
                    FalseForm,
                    render_kw={"id": f"{self.variablename}_false_{fieldid}"},
                )
                fieldid += 1
        if self.whentrue:
            for wt in self.whentrue:
                TrueForm = wf.populateFlaskForm(
                    TrueForm,
                    render_kw={"id": f"{self.variablename}_true_{fieldid}"},
                )
                fieldid += 1
        setattr(
            form,
            self.variablename,
            BooleanField(
                self.message,
                default=self.default,
                render_kw={"onchange": "toggle_questions(this);"},
            ),
        )
        setattr(form, f"{self.variablename}_trueform", FormField(TrueForm, label=""))
        setattr(form, f"{self.variablename}_falseform", FormField(FalseForm, label=""))
        return form


class Const(QuestionBase):
    """Sets the variable to the `default` value. Doesn't show anything.

    :param variablename: The variable name to set
    :param message: Message to show
    :param default: Value that variable is set to
    """

    def __init__(self, variablename, default):
        super().__init__(variablename, None, default)

    def toInquirerQuestion(self, ignore=False):
        """Returns an inquirer package version of this question."""
        return inquirer.Text(
            self.variablename, message="", default=self.default, ignore=True,
        )

    def populateFlaskForm(self, form, render_kw=None):
        """Returns a version of the recieved FlaskForm, populated by info from this object.

        :param FlaskForm form: The form to populate
        :param render_kw: extra attributes to include
        :returns: Form with all the fields
        :rtype: FlaskForm"""
        setattr(
            form,
            self.variablename,
            HiddenField(self.variablename, default=self.default),
        )
        return form


def prompt(questions, use_defaults=False):
    """Baseclass for questions.
    All questions have variablename, message and an optional default.

    :param list[jobbergate.jobInquirer.QuestionBase] questions: list of questions
    :param use_defaults: option to use default value instead of asking, when possible
    :returns: dictionary full of answers
    """
    retval = {}
    inquirer_questions = []

    for question in questions:
        if use_defaults and question.default is not None:
            retval.update({question.variablename: question.default})
            print(f"Default used: {question.variablename}={question.default}")
        else:
            iq = question.toInquirerQuestion()
            if isinstance(iq, (list, tuple)):
                inquirer_questions.extend(iq)
            else:
                inquirer_questions.append(iq)

    retval.update(inquirer.prompt(inquirer_questions))
    return retval
