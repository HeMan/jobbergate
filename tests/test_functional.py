from jobbergate import cli, create_app


def get_result(cmds, testname, arguments=None):
    for cmd in cmds:
        if cmd.name == testname:
            if arguments is None:
                arguments = ["-"]
            app = create_app()
            runner = app.test_cli_runner()
            result = runner.invoke(cmd, arguments)
            return result
    raise ModuleNotFoundError


def test_find_application_no_view():
    result = get_result(cli.cmds, "test_find_application_no_view")
    assert isinstance(result.exception, ModuleNotFoundError)


def test_find_application_no_mainflow():
    result = get_result(cli.cmds, "test_find_application_no_mainflow")
    assert isinstance(result.exception, AttributeError)


def test_find_application_with_mainflow():
    result = get_result(cli.cmds, "test_find_application_with_mainflow")
    assert result.output == "10"
