from jobbergate.cli import flatten, parse_field, ask_questions
import inquirer
from jobbergate import appform


def test_flatten():
    assert flatten([1, 2, [3, 4]]) == [1, 2, 3, 4]


def test_parse_field():
    textfield = parse_field(appform.Text("var", "Variable"))
    assert isinstance(textfield, inquirer.Text)
    assert textfield.name == "var"


def test_ask_questions(mocker):
    def side_effect(inlist):
        retval = {}
        for i in inlist:
            retval[i.name] = i.message
        return retval

    mocker.patch.object(inquirer, "prompt")
    inquirer.prompt.side_effect = side_effect
    questions = ask_questions(
        [appform.Text("var", "Variable"), appform.Integer("int", "Integer")], {}
    )
    assert questions == {"var": "Variable", "int": "Integer"}
