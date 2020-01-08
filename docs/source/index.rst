Welcome to Jobbergate's documentation!
======================================

Workflow
--------
Simple workflow
~~~~~~~~~~~~~~~
A simple workflow is implemented with the function `mainflow` defined in `views.py` and a template defined in `templates/job_template.j2`::

  +-- views.py
  +-+ templates/
    + job_template.j2

views.py:

.. code-block:: python

  from jobbergate import appform

  def mainflow(data):
      return [appform.Text("jobname", "What is the jobname?", default="simulation")]

job_template.j2:

.. code-block:: jinja

  #!/bin/bash
  #SBATCH -j {{ job.jobname }}
  sleep 30

Workflow with implicit workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A workflow with implicit workflows is built by defining `mainflow` and functions decorated with `appform.workflow`::

  +-- views.py
  +-+ templates/
    + job_template.j2

views.py:

.. code-block:: python

  from jobbergate import appform

  def mainflow(data):
      return [appform.Text("jobname", "What is the jobname?", default="simulation")]

  @appform.workflow
  def debug(data):
      return [appform.Confirm("debug", "Add debug info?")]

  @appform.workflow
  def gpu(data):
      return [appform.Integer("gpus", "Number of gpus?", default=1, maxval=10)]

job_template.j2:

.. code-block:: jinja

  #!/bin/bash
  #SBATCH -j {{ job.jobname }}


  {% if job.gpus %}
  NUMBER_OF_GPUS={{ job.gpus }}
  {% else %}
  NUMBER_OF_GPUS=0
  {% endif %}

  {% if job.debug %}
  /application/debug_prepare
  {% endif %}

  /application/run_application -gpus $NUMBER_OF_GPUS

Templates
---------


Questions
---------
All questions has an variable name and a message (except Const), and could have a default value.

appform.Text(variablename, message, default=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Asks for a text value.

appform.Integer(variablename, message, minval=None, maxval=None, default=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Asks for an integer value. Could have min and/or max constrains.

appform.List(variablename, message, choices, default=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gives the user a list to choose one from.

appform.Directory(variablename, message, default=None, exists=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Asks for a directory name. If `exists` is `True` it checks if path exists and is a directory.

appform.File(variablename, message, default=None, exists=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Asks for a file name. If `exists` is `True` it checks if path exists and is a file.

appform.Checkbox(variablename, message, choices, default=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gives the user a list to choose multiple entries from.

appform.Confirm(variablename, message, default=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Asks a question with an boolean answer (true/false).

appform.BooleanList(variablename, message, default=None, whentrue=None, whenfalse=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gives the use a boolean question, and depending on answer it shows `whentrue` or `whenfalse` questions. `whentrue` and `whenfalse` are lists with questions. Could contain multiple levels of BooleanLists.

appform.Const(variablename, default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sets the variable to the `default` value. Doesn't show anything.

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
