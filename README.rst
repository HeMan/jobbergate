Jobbergate
==========

.. image:: https://img.shields.io/pypi/v/jobbergate.svg
    :target: https://pypi.python.org/pypi/jobbergate/
.. image:: https://travis-ci.com/HeMan/jobbergate.svg?branch=master
    :target: https://travis-ci.com/HeMan/jobbergate
.. image:: https://readthedocs.org/projects/jobbergate/badge/?version=stable
    :target: https://jobbergate.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation Status
    
Jobbergate is a questionnaire application that populates Jinja2 templates with given answers.

In its simplest form you only need a `views.py` that defines `mainflow` and a 
template file (called `templates/job_template.j2`) which gets populated with your answers.
To support advanced workflows you could define multiple levels of questions, change 
to other templates, run functions before and after subworkflows, have follow up questions to boolean questions and so on.

To install, just do::

    pip install jobbergate

Configure jobbergate.yaml to point to your directory where you have all
applications. Set ``JOBBERGATE_PATH`` environment to point to where your
jobbergate.yaml resides.

Jobbergate is a Flask application but could be run both as a web application
and as a cli application.

To run as web application, just do::

    flask run

To run as cli application, you can find out which applications it has in its
configuration directory with::

    flask --help

If you have an application called `simple` you run it with::

    flask simple outputfile.sh

This will populate the simple application template with the answers you give in
the following interactive session, and create ``outputfile.sh``.

If you want the output file to be run in bash automatically, you may explicitly give the command in your
implemented application. For example, if you define a function in your application's ``controller.py`` such as::

    @workflow.logic
    def post_generic(data):
        retval = {"cmd_command":f"cat {data['filename']}"}
        return retval

the application will run::

    cat outputfile.sh

which shows the content of the output file.
This feature can be suppressed by using the '--no-cmd' flag::

    flask simple outputfile.sh --no-cmd
