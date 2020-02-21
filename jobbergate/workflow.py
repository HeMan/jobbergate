"""
Workflow
========

Work flow module that could add pre and post functions to workflows"""

from functools import partial, wraps

prefuncs = {}
postfuncs = {}


def logic(func=None, *, name=None, prepost=None):
    """A decorator that registers functions as either pre or post to workflows.

    :param name: (optional) Descriptive name that is used when choosing workflow


    Hooking a pre-function to eigen implicit by function name:

    .. code-block:: python

        # Hooking pre function to `eigen` implicit by function name
        @logic
        def pre_eigen(data):
            print("Pre function to `eigen` questions")


    Explicit hooking post function to `eigen` workflow:

    .. code-block:: python

        @logic(name="eigen", prepost="post")
        def myfunction(data):
            print("Post function to `eigen` questions")

    Pre and post that are run before and after all questions, respectively:

    .. code-block:: python

        @logic
        def pre_(data):
            print("Pre function that runs before any question")

        @logic()
        def post_(data):
            print("Post function that is run after all questions")
    """
    if func is None:
        return partial(logic, name=name, prepost=prepost)

    @wraps(func)
    def wrapper(*args, **kvargs):
        return func(*args, **kvargs)

    if name is None:
        if func.__name__.startswith("pre_"):
            name = func.__name__[4:]
            prepost = "pre"

        if func.__name__.startswith("post_"):
            name = func.__name__[5:]
            prepost = "post"

    if prepost == "pre":
        prefuncs[name] = func
        return wrapper

    if prepost == "post":
        postfuncs[name] = func
        return wrapper

    raise NameError
