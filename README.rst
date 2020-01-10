Jobbergate
==========

Jobbergate is an questionnaire application that populates Jinja2 templates with given answers.

In its simplest form you only need a `views.py` that defines `mainflow` and a template file (called `templates/job_template.j2`) which gets populated with your answers.
To support advanced workflows you could define multiple levels of questions, change to other templates, run functions before and after subworkflows, have follow up questions to boolean questions and so on.
