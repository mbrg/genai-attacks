import pytest
from test_utils import *


@pytest.mark.parametrize("json_object_path", OBJECT_FILE_NAMES)
@load_json_object_wrapper
def test_object_name_and_id_align(obj):
    cleaned_object_id = obj["$id"].replace("_", " ").split("/")[-1]
    cleaned_name = (
        obj["name"].replace("-", " ").replace("'", "").replace(":", "").lower()
    )

    assert cleaned_name.startswith(
        cleaned_object_id
    ), f"Object $id should be a prefix of its name. For example, an object with id $gai-technique/an_example should be named either An Example or An-Example"
