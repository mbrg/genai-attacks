import json
import os

OBJECT_TYPES = ["tactic", "technique", "procedure", "platform", "entity"]

OBJECT_FILE_NAMES = []
for object_type in OBJECT_TYPES:
    for name in os.listdir(object_type):
        OBJECT_FILE_NAMES.append(os.path.join(object_type, name))


def load_json_object(func):
    def _func(json_object_path, *args, **kwargs):
        with open(json_object_path, "r") as fp:
            obj = json.load(fp)
        return func(obj, *args, **kwargs)

    return _func
