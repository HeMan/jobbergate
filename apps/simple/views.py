from jobbergate import appform

appform.Text("jobname", "Name of job", default="my-job")
appform.Integer("memory", "Max memory needed (GB)", minval=0, maxval=1000, default=10)


@appform.workflow()
def debug():
    pass


@appform.workflow("""This is the Eigen value workflow""")
def eigen():
    appform.Integer("eigenvalue", "What is the eigenvalue", default=10)
