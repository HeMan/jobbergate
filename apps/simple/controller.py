# from jobbergate.workflow import logic
from jobbergate import workflow


@workflow.logic
def pre_debug(data):
    print("pre debug")
    print(data)
    return {"more": "info"}


@workflow.logic
def post_debug(data):
    print("Post debug")
    print(data)


@workflow.logic
def pre_():
    print("Pre")
