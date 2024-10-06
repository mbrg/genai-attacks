import pytest
from test_utils import *


@pytest.mark.parametrize("json_object_path", OBJECT_FILE_NAMES)
def test_object_file_name_and_id_align(json_object_path):
    obj = load_json_object(json_object_path)
    obj_id = obj["$id"].split("/")[-1]
    file_name = json_object_path.split("/")[-1].split(".")[0]
    assert (
        obj_id == file_name
    ), "Object $id should align to its filename. For example, an object with id $gai-technique/example should have file name example.json"
