import pytest
from test_utils import *


@pytest.mark.parametrize("json_object_path", OBJECT_FILE_NAMES)
@load_json_object
def test_multi_line_code_block_new_line_wrappers(obj):
    # get the description as a series of non-code-block, code-block segments
    desc = obj.get("description", "")
    split_by_long_code_block = desc.split("```")

    assert (
        len(split_by_long_code_block) % 2 == 1
    ), f'Description has an odd number of "```" characters: {split_by_long_code_block}'

    for _, code_block in zip(
        split_by_long_code_block[0::2], split_by_long_code_block[1::2]
    ):
        assert code_block[0] == "\n", "Multi-line code block must start with \\n"
        assert code_block[-1] == "\n", "Multi-line code block must end with \\n"
