"""Abstraction layer for questions"""

from collections import deque
from functools import partial, wraps


questions = deque()
workflows = {}


def Text(variablename, message, default=None):
    """Adds a text question"""
    questions.append(
        {
            "type": "Text",
            "variablename": variablename,
            "message": message,
            "default": default,
        }
    )


def Integer(variablename, message, minval=None, maxval=None, default=None):
    """Adds a integer question. Supports min and max checks"""
    questions.append(
        {
            "type": "Integer",
            "variablename": variablename,
            "message": message,
            "minval": minval,
            "maxval": maxval,
            "default": default,
        }
    )


def List(variablename, message, choices, default=None):
    """Adds a list to select from"""
    questions.append(
        {
            "type": "List",
            "variablename": variablename,
            "message": message,
            "choices": choices,
            "default": default,
        }
    )


def Directory(variablename, message, default=None, exists=None):
    """Adds a question for path. Checks that given path is directory if it
    should exist"""
    questions.append(
        {
            "type": "Directory",
            "variablename": variablename,
            "message": message,
            "default": default,
            "exists": exists,
        }
    )


def File(variablename, message, default=None, exists=None):
    """Adds a question for path. Checks that given path is a file if it should
    exist"""
    questions.append(
        {
            "type": "File",
            "variablename": variablename,
            "message": message,
            "default": default,
            "exists": exists,
        }
    )


def Checkbox(variablename, message, choices, default=None):
    """Adds a multiple choice list"""
    questions.append(
        {
            "type": "Checkbox",
            "variablename": variablename,
            "message": message,
            "choices": choices,
            "default": default,
        }
    )


def Confirm(variablename, message, default=None):
    """Adds a boolean question which returns true or false"""
    questions.append(
        {
            "type": "Confirm",
            "variablename": variablename,
            "message": message,
            "default": default,
        }
    )


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
