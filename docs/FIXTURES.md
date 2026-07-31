# Fixture design guide

CrossViewLab treats every input as an exported artifact. It never decides how an
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

## Interpreting findings

A cross-view discrepancy is ambiguous by design. Collection timing, permissions,
PID reuse, exporter bugs, software updates, instrumentation, and actual tampering
can all produce similar observations. Use CrossViewLab to make the discrepancy
reproducible, then corroborate it with authorized evidence from your environment.
