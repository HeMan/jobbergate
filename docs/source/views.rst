Views
======

Simple view (with no workflow selection)
----------------------------------------

Views is built functions returning lists of questions. ``mainflow`` is the only
expected function, others are all optional.

Functions that jobbergate calls gets all know data as inparameter as `data`.

Simplest `view.py`:

.. code-block:: python

    from jobbergate import appform

    def mainflow(data):
        return [appform.Text('jobbname', 'What is the jobbname', default='MyJob')]


View with decorator workflow
----------------------------

Views can have a workflow "split" that gives the user an option to select
a diferent path.

'view.py' with workflow defined with decorator. This give the user the question
to select between debug and precision workflow. debug gives the boolean question
"Add extra debug flags" and precsision gives an integer question regarding
"Steps per mm".

.. code-block:: python

    from jobbergate import appform

    def mainflow(data):
        return [appform.Text('jobbname', 'What is the jobbname', default='MyJob')]

    @appform.workflow
    def debug(data):
        return [appform.Confirm('debugoptions', 'Add extra debug flags')]

    @appform.workflow
    def precision(data):
        return [appform.Integer('precision', 'Steps per mm', minval=1, maxval=100)]


View with ``nextworkflow`` question
-----------------------------------

A view can have workflow selected by a question with the variable
``nextworkflow``. This should be a List to give the user a list to select from.
This should not have any function decorated with ``@appform.workflow``.

.. code-block:: python

    from jobbergate import appform

    def mainflow(data):
        return [appform.Text('jobbname', 'What is the jobbname'),
                appform.List('nextworkflow', ['precision', 'debug'])]

    def debug(data):
        return [appform.Confirm('debugoptions', 'Add extra debug flags')]

    def precision(data):
        return [appform.Integer('precision', 'Steps per mm', minval=1, maxval=100)]
