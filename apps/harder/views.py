from jobbergate import appform

appform.Text("jobname", "Name of job", default="my-job")
appform.Integer("memory", "Max memory needed (GB)", minval=0, maxval=1000, default=10)
appform.List(
    "timelimit",
    "Set timelimit (hours)",
    choices=[1, 2, 3, 4, 5, 6, 7, 8, 12, 24],
    default=1,
)
appform.List(
    "workflow",
    message="What do you want to do?",
    choices=[("Debug session", "debug"), ("Run femfat", "run")],
    default="run",
)
appform.Directory(
    "scratch", message="Path to shared scratch directory (absolute path)", exists=False
)

appform.File("ffjfile", message="FFJ input file (absolute path)", exists=True)

appform.Checkbox("multi", message="Choose many", choices=["ett", "två", "tre", "fyra"])
appform.Confirm("gpus", message="Should GPUs be used?", default=True)
