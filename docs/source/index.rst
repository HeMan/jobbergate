.. include:: ../../README.rst

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

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   API
   internal



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
