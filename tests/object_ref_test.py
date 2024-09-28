import pytest
from test_utils import *


@pytest.mark.parametrize("json_object_path", OBJECT_FILE_NAMES)
@load_json_object_wrapper
def test_reference_is_valid(obj):
    for ref in obj.get("object_references", []):
        ref_file_name = ref["$id"].replace("$gai-", "") + ".json"
        assert (
            ref_file_name in OBJECT_FILE_NAMES
        ), f"Object {obj['$id']} has invalid reference to {ref['$id']}"
