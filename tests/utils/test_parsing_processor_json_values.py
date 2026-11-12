"""Valid JSON must survive structured-output cleanup without data loss."""

import json

import pytest

from agentforge.utils.parsing_processor import ParsingProcessor


@pytest.mark.parametrize(
    "value",
    [
        [{"name": "first"}],
        [{"name": "first"}, {"name": "second"}],
        {"text": ",}"},
        {"text": ",]"},
        '{"name": "quoted object"}',
        {"nested": [{"text": "a,}b"}]},
        [],
        42,
    ],
)
@pytest.mark.parametrize("fenced", [False, True])
def test_parse_preserves_valid_json_values(value, fenced):
    content = json.dumps(value)
    if fenced:
        content = f"```json\n{content}\n```"

    assert ParsingProcessor().parse_by_format(content, "json") == value


def test_malformed_json_can_still_use_cleanup():
    content = '```json\n{"name": "first",}\n```'

    assert ParsingProcessor().parse_by_format(content, "json") == {"name": "first"}
