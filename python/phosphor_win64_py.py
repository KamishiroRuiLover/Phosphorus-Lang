import sys
import os
import json


# Classes
class PT2token:
    def __init__(self, spec_type, argument = ""):
        self.type = spec_type
        self.arg: str = argument
    def __repr__(self):
        return f"Token: {self.type}, {self.arg}"


# Globals
MAIN_PROJ_DIR = ""
PROJ_DETAILS = ""

SPECIAL_CHARS = [
    "(",
    ")",
    "[",
    "]",
    ";",
    "{",
    "}"
]

NOARGS_KEYWORDS_DICT = {
    "{": "ph_funcContOpen",
    "}": "ph_funcContClosed",
    "(": "ph_argumentsOpen",
    ")": "ph_argumentsClosed",
    ";": "ph_endLine",
    "+": "ph_mathAdd",
    "-": "ph_mathSub",
    "*": "ph_mathMul",
    "/": "ph_mathDiv",
    "^": "ph_mathExp"
}

LANGFUNC_KEYWORDS_DICT = {
    "return": {
        "name": "ph_return",
        "type": "get_arg"
    },
    "public": {
        "name": "ph_classFuncID",
        "type": "name"
    },
    "private": {
        "name": "ph_classFuncID",
        "type": "name"
    },
    "static": {
        "name": "ph_classType",
        "type": "name"
    },
    "abstract": {
        "name": "ph_classType",
        "type": "name"
    }
}

FUNCS_DICT = {
}

CLASSES_DICT = {
}


def main():
    if len(sys.argv) != 2:
        print("USAGE:\nphosphor_win64_py <INPUT DIRECTORY>")
        sys.exit(1)
    global MAIN_PROJ_DIR
    global PROJ_DETAILS
    MAIN_PROJ_DIR = sys.argv[1]

    PROJ_DETAILS = json.loads(open(find_phproj(MAIN_PROJ_DIR)).read())

    # get content of a script: open(os.path.join(MAIN_PROJ_DIR, PROJ_DETAILS["scripts"][0])).read()

    tokens = lexer_pt3(lexer_pt2(lexer_pt1(open(os.path.join(MAIN_PROJ_DIR, PROJ_DETAILS["scripts"][0])).read())))
    print(tokens)


def find_phproj(path):
    for i in os.listdir(path):
        if os.path.splitext(i)[1] == ".phproj":
            return os.path.join(path, i)

    print("PROJECT DID NOT CONTAIN .phproj\n(did you put it in the exact project folder?)")
    exit(2)


def is_float(number):
    try:
        float(number)
        return True
    except ValueError:
        return False


def get_objs(content):
    temp = ""
    objects = []

    for i in content:
        if i != ".":
            temp += i
        else:
            objects.append(PT2token("pre_misc", temp))
            temp = ""

    if temp != "":
        objects.append(PT2token("pre_misc", temp))

    return objects


def lexer_pt1(content):
    tokens = []

    i = 0
    temp = ""
    while i < len(content):
        if content[i].isalnum() or content[i] == ".":
            temp += content[i]
        elif content[i].isspace():
            if temp != "":
                tokens.append(temp)
                temp = ""
        elif content[i] in SPECIAL_CHARS:
            if temp != "":
                tokens.append(temp)
                temp = ""
            tokens.append(content[i])
        elif content[i] == '"':
            if temp != "":
                tokens.append(temp)
                temp = ""
            tokens.append('"')
            i += 1
            while content[i] != '"':
                temp += content[i]
                i += 1
            tokens.append(temp)
            tokens.append('"')

        i += 1

    return tokens


def lexer_pt2(og_list):
    tokens = []

    i = 0
    while i < len(og_list):
        if og_list[i] in NOARGS_KEYWORDS_DICT:
            tokens.append(PT2token(NOARGS_KEYWORDS_DICT[og_list[i]]))
        elif og_list[i] == '"':
            temp = ""

            i += 1
            while og_list[i] != '"':
                temp += og_list[i]
                i += 1

            tokens.append(PT2token("ph_strLit", temp))
        elif og_list[i].isdigit():
            tokens.append(PT2token("ph_intLit", og_list[i]))
        elif is_float(og_list[i]):
            tokens.append(PT2token("ph_fltLit", str(float(og_list[i]))))
        else:
            tokens.append(PT2token("pre_misc", og_list[i]))
        i += 1

    return tokens


def lexer_pt3(og_list):
    tokens = []

    i = 0
    while i < len(og_list):
        if og_list[i].type == "pre_misc" and "." in og_list[i].arg:
            for j in get_objs(og_list[i].arg):
                tokens.append(j)
        else:
            tokens.append(og_list[i])

        i += 1

    return tokens


def lexer_pt4(og_list):
    tokens = []

    i = 0
    while i < len(og_list):
        if og_list[i].type == "pre_misc":
            if og_list[i].arg in LANGFUNC_KEYWORDS_DICT:
                temp = PT2token(LANGFUNC_KEYWORDS_DICT[og_list[i].arg].name)
                if LANGFUNC_KEYWORDS_DICT[og_list[i]].type == "name":
                    temp.arg = og_list[i].arg
                elif LANGFUNC_KEYWORDS_DICT[og_list[i]].type == "get_arg":
                    i += 1
                    if og_list[i].type != "ph_argumentsOpen":
                        print("ERROR: function did not define argument")

                tokens.append(temp)


main()