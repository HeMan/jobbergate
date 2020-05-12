"""
Appform
=======

Abstraction layer for questions. """

from collections import deque
from functools import partial, wraps


questions = deque()
workflows = {}


def workflow(func=None, *, name=None):
    """A decorator for workflows. Adds an workflow question and all questions
    added in the decorated question is asked after selecting workflow.

    :param name: (optional) Descriptional name that is shown when choosing workflow

    Add a workflow named debug:

    .. code-block:: python

        @workflow
        def debug(data):
            return [jobInquirer.File("debugfile", "Name of debug file")]

    Add a workflow with longer name:

    .. code-block:: python

        @workflow(name="Secondary Eigen step")
        def 2ndstep(data):
            return [jobInquirer.Text("eigendata", "Definition of eigendata")]
    """

    if func is None:
        return partial(workflow, name=name)

    @wraps(func)
    def wrapper(*args, **kvargs):
        return func(*args, **kvargs)

    workflows[name or func.__name__] = func

    return wrapper
