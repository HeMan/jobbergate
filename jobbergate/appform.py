"""Abstraction layer for questions"""

from collections import deque
from functools import partial, wraps


questions = deque()
workflows = {}


class QuestionBase:
    def __init__(self, variablename, message, default):
        self.variablename = variablename
        self.message = message
        self.default = default


class Text(QuestionBase):
    def __init__(self, variablename, message, default=None):
        super().__init__(variablename, message, default)


class Integer(QuestionBase):
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


class List(QuestionBase):
    def __init__(self, variablename, message, choices, default=None):
        super().__init__(variablename, message, default)
        self.choices = choices


class Directory(QuestionBase):
    def __init__(self, variablename, message, default=None, exists=None):
        super().__init__(variablename, message, default)
        self.exists = exists


class File(QuestionBase):
    def __init__(self, variablename, message, default=None, exists=None):
        super().__init__(variablename, message, default)
        self.exists = exists


class Checkbox(QuestionBase):
    def __init__(self, variablename, message, choices, default=None):
        super().__init__(variablename, message, default)
        self.choices = choices


class Confirm(QuestionBase):
    def __init__(self, variablename, message, default=None):
        super().__init__(variablename, message, default)


class BooleanList(QuestionBase):
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


class Const(QuestionBase):
    def __init__(self, variablename, default):
        super().__init__(variablename, None, default)


def workflow(func=None, *, name=None):
    """Decorator for workflows. Adds an workflow question and all questions
    added in the decorated question is asked after selecting workflow.

    # Add a workflow named debug:
    @workflow
    def debug(data):
        appform.File("debugfile", "Name of debug file")

    # Add a workflow with longer name
    @workflow(name="Secondary Eigen step")
    def 2ndstep(data):
        appform.Text("eigendata", "Definition of eigendata")
    """

    if func is None:
        return partial(workflow, name=name)

    @wraps(func)
    def wrapper(*args, **kvargs):
        return func(*args, **kvargs)

    workflows[name or func.__name__] = func

    return wrapper
