import json
import os

OBJECT_TYPES = ["tactic", "technique", "procedure", "platform", "entity", "mitigation"]

OBJECT_FILE_NAMES = []
for object_type in OBJECT_TYPES:
    for name in os.listdir(object_type):
        OBJECT_FILE_NAMES.append(os.path.join(object_type, name))


def load_json_object(json_object_path):
    with open(json_object_path, "r") as fp:
        obj = json.load(fp)
    return obj


def load_json_object_wrapper(func):
    def _func(json_object_path, *args, **kwargs):
        obj = load_json_object(json_object_path)
        return func(obj, *args, **kwargs)

    return _func
