# Jobbergate
Jobbergate is an questionaire application that populates Jinja2 templates with given answers.

In it's simplest form you only need a `views.py` that defines `mainflow` and a template file (called `tempates/job_template.j2`) which gets populate with your answers.
To support advanced workflows you could define multiple levels of questions, change to other templates, run functions before and after subworkflows, have follow up questions to boolean questions and so on.

## Workflow
### Simple workflow
A simple workflow is implemented with the function `mainflow` defined in `views.py` and a template defined in `templates/job_template.j2`


<pre>+-- views.py
+-+ templates/
  + job_template.j2
</pre>
views.py
```python
from jobbergate import appform

def mainflow(data):
    return [appform.Text("jobname", "What is the jobname?", defaut="simulation")]
```

job_template.j2
```jinja2
#!/bin/bash
#SBATCH -j {{ job.jobname }}
sleep 30
```

### Workflow with implicit workflows
A workflow with implicit workflows is built by defining `mainflow` and functions decorated with `appform.workflow`.
<pre>+-- views.py
+-+ templates/
  + job_template.j2
</pre>

views.py
```python
from jobbergate import appform

def mainflow(data):
    return [appform.Text("jobname", "What is the jobname?", default="simulation")]

@appform.workflow
def debug(data):
    return [appform.Confirm("debug", "Add debug info?")]

@appform.workflow
def gpu(data):
    reuturn [appform.Integer("gpus", "Number of gpus?", default=1, maxval=10)]
```

job_template.j2
```jinja2
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
```
## Templates


## Questions
All questions has an variable name and a message (execpt Const), and could have a defaut value.
### appform.Text(variablename, message, default=None)
Asks for a text value.

### appform.Integer(variablename, message, minval=None, maxval=None, default=None)
Asks for an integer value. Could have min and/or max constrains.

### appform.List(variablename, message, choices, default=None)
Gives the user a list to choose one from.

### appform.Directory(variablename, message, default=None, exists=None)
Asks for a directory name. If `exists` is `True` it checks if path exists and is a directory.

### appform.File(variablename, message, default=None, exists=None)
Asks for a file name. If `exists` is `True` it checks if path exists and is a file.

### appform.Checkbox(variablename, message, choices, default=None)
Gives the user a list to choose multiple entries from.

### appform.Confirm(variablename, message, default=None)
Asks a question with an boolean answer (true/false).

### appform.BooleanList(variablename, message, default=None, whentrue=None, whenfalse=None)
Gives the use a boolean question, and depending on answer it shows `whentrue` or `whenfalse` questions. `whentrue` and `whenfalse` is lists with questions. Could contain multiple levels of BooleanList's.

### appform.Const(variablename, default)
Sets the variable to the `default` value. Doesn't show anything.
