"""Abstraction layer for questions"""

questions = []


def Text(variablename, message, default=None):
    questions.append(
        {
            "type": "Text",
            "variablename": variablename,
            "message": message,
            "default": default,
        }
    )


def Integer(variablename, message, minval=None, maxval=None, default=None):
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
    questions.append(
        {
            "type": "Confirm",
            "variablename": variablename,
            "message": message,
            "default": default,
        }
    )
