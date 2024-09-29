import pytest
from test_utils import *


def _validate_referenced_object_id(ref_obj_id):
    ref_file_name = ref_obj_id.replace("$gai-", "") + ".json"
    assert (
        ref_file_name in OBJECT_FILE_NAMES
    ), f"Invalid reference to object id: {ref_obj_id}"


@pytest.mark.parametrize("json_object_path", OBJECT_FILE_NAMES)
@load_json_object_wrapper
def test_object_references(obj):
    for ref in obj.get("object_references", []):
        _validate_referenced_object_id(ref["$id"])
