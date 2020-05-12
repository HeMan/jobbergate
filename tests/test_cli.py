from jobbergate.cli import flatten, ask_questions
import inquirer
from jobbergate import jobInquirer


def test_flatten():
    assert flatten([1, 2, [3, 4]]) == [1, 2, 3, 4]


def test_inquirer_conversion():
    textfield = jobInquirer.Text("var", "Variable").toInquirerQuestion()
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
        [jobInquirer.Text("var", "Variable"), jobInquirer.Integer("int", "Integer")], {}
    )
    assert questions == {"var": "Variable", "int": "Integer"}
