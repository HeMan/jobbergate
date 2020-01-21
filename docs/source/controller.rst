Controller
==========

Controller is for running code before and after workflows run.

All ``pre_``/``post_``-functions takes a dict as an argument that is populated with all
cumulated info from earlier ``pre_``/``post_``, all previous questions and configuration file.

Should return a dict or ``None``.


.. code-block:: python

   
    from datetime import datetime
    from jobbergate import workflow

    @workflow.logic
    def pre_(data):
       # adds current datetime to data
       return {'datetime': str(datetime.now())}



