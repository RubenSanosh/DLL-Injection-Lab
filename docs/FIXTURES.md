# Fixture design guide

DLL Injection Lab treats every artifact-mode input as an exported artifact. It never decides how an
artifact was acquired and never attempts acquisition itself.

## Inventory contract

- The document root must be a JSON object.
- `source` must be a non-empty string that identifies the exporter or fixture.
- `processes` must be an array.
- Every process must have a unique non-negative integer `pid`.
- `name`, `ppid`, `path`, `user`, and `command_line` are optional comparison
  fields. A field is compared only when both views provide it.

Use fictional names, synthetic URIs, and non-sensitive command lines in public
fixture packs. Keep acquisition timestamps and exporter versions in a separate
lab manifest until the report schema adds provenance fields.

## Entry-byte contract

- `source` must be a non-empty string.
- `samples` must be an array.
- Each sample requires `component`, `symbol`, and `observed_hex`.
- `baseline_hex` is optional. When present, an exact normalized comparison is
  performed.
- Hex strings may use spaces, colons, underscores, hyphens, and `0x` prefixes.
  Invalid characters and odd-length values are rejected rather than silently
  repaired.

## Build a useful test pack

Include at least four cases:

1. Identical inventories with no findings.
2. One baseline-only record.
3. One observed-only record or one shared-PID field mismatch.
4. Clean and intentionally altered entry-byte samples.

For each intentionally altered sample, document the expected rule ID. Always
validate a generated JSON report against `schemas/report.schema.json`.

## Invalid event-stream fixtures

`fixtures/invalid/` contains small JSONL files that are expected to fail
validation in `load_event_stream`. They exist so contributors have reusable,
public examples of the validation boundary instead of only inline test data.

| File | What's wrong |
|---|---|
| `malformed_json.jsonl` | Not valid JSON (an unquoted object key) |
| `missing_required_field.jsonl` | A required string field (`module`) is empty |
| `invalid_pid.jsonl` | A PID field (`actor_pid`) is negative |

Each file is used in a parametrized test asserting the specific `InputError`
message it should raise. If you add a new invalid fixture, add a row here and
a corresponding test case.

## Interpreting findings

A cross-view discrepancy is ambiguous by design. Collection timing, permissions,
PID reuse, exporter bugs, software updates, instrumentation, and actual tampering
can all produce similar observations. Use DLL Injection Lab to make the discrepancy
reproducible, then corroborate it with authorized evidence from your environment.
