questions = []


def Text(variablename, question, default=None):
    questions.append({"variablename": variablename, "question": question})


def Integer(variablename, question, minval=None, maxval=None, default=None):
    questions.append({"variablename": variablename, "question": question})
