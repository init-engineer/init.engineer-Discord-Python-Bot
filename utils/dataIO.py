import json


def change_value(file: str, value: str, changeto: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("您嘗試讀取的文件不存在 ...")

    data[value] = changeto
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)


def append_value(file: str, value: str, addition: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("您嘗試讀取的文件不存在 ...")

    data[value].append(addition)
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)
