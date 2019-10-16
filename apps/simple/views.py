import appform

ask_jobname = appform.Text("jobname", "Name of job", default="my-job")
ask_memory = appform.Integer(
    "memory", "Max memory needed (GB)", minval=0, maxval=1000, default=10
)
