from crossview_lab.detectors import compare_inventories, inspect_entry_bytes


def inventory(source, *processes):
    return {"source": source, "processes": list(processes)}


def test_clean_inventories_have_no_findings():
    baseline = inventory("baseline", {"pid": 7, "name": "same.exe", "ppid": 1})
    observed = inventory("observed", {"pid": 7, "name": "same.exe", "ppid": 1})

    assert compare_inventories(baseline, observed) == []


def test_cross_view_comparison_reports_missing_and_changed_records():
    baseline = inventory(
        "baseline",
        {"pid": 7, "name": "worker.exe", "ppid": 1},
        {"pid": 8, "name": "baseline-only.exe"},
    )
    observed = inventory(
        "observed",
        {"pid": 7, "name": "renamed.exe", "ppid": 1},
        {"pid": 9, "name": "observed-only.exe"},
    )

    findings = compare_inventories(baseline, observed)

    assert [finding["type"] for finding in findings] == [
        "missing-from-observed-inventory",
        "missing-from-baseline-inventory",
        "inventory-field-mismatch",
    ]
    assert findings[2]["evidence"]["fields"]["name"] == {
        "baseline": "worker.exe",
        "observed": "renamed.exe",
    }


def test_fields_missing_from_one_export_are_not_false_mismatches():
    baseline = inventory("baseline", {"pid": 7, "name": "same.exe", "path": "x"})
    observed = inventory("observed", {"pid": 7, "name": "same.exe"})

    assert compare_inventories(baseline, observed) == []


def test_entry_byte_inspection_reports_baseline_difference_and_prefix():
    artifact = {
        "source": "fixture",
        "samples": [
            {
                "component": "ntdll",
                "symbol": "SyntheticEntry",
                "baseline_hex": "4c8bd1",
                "observed_hex": "e90000",
            }
        ],
    }

    findings = inspect_entry_bytes(artifact)

    assert [finding["type"] for finding in findings] == [
        "entry-bytes-differ-from-baseline",
        "relative-jump-at-entry",
    ]


def test_jump_byte_later_in_a_clean_entry_is_not_flagged_as_entry_jump():
    artifact = {
        "source": "fixture",
        "samples": [
            {
                "component": "ntdll",
                "symbol": "SyntheticCleanEntry",
                "observed_hex": "4c8bd1e9000000",
            }
        ],
    }

    assert inspect_entry_bytes(artifact) == []
