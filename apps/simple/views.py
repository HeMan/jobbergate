from jobbergate import appform

appform.Text("jobname", "Name of job", default="my-job")
appform.Integer("memory", "Max memory needed (GB)", minval=0, maxval=1000, default=10)
