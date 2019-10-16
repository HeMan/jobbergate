questions = []


def Text(variablename, question, default=None):
    questions.append({"variablename": variablename, "question": question})
    print(variablename, question, default)


def Integer(variablename, question, minval=None, maxval=None, default=None):
    questions.append({"variablename": variablename, "question": question})
    print(variablename, question, minval, maxval, default)
