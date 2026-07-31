import json

import pytest

from crossview_lab.errors import InputError
from crossview_lab.io import load_inventory, normalize_hex


def test_normalize_hex_accepts_common_export_separators():
    assert normalize_hex("0x4C 0x8B-D1:00") == "4c8bd100"


@pytest.mark.parametrize("value", ["", "0xGG", "abc", "90 zz"])
def test_normalize_hex_rejects_ambiguous_or_malformed_values(value):
    with pytest.raises(InputError):
        normalize_hex(value)


def test_inventory_rejects_duplicate_pids(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text(
        json.dumps({"source": "fixture", "processes": [{"pid": 7}, {"pid": 7}]}),
        encoding="utf-8",
    )

    with pytest.raises(InputError, match="duplicate PID 7"):
        load_inventory(path)


def test_inventory_rejects_non_object_json(tmp_path):
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(InputError, match="JSON object"):
        load_inventory(path)
