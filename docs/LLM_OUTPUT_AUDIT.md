# Local-LLM output audit

CrossViewLab grew out of an experiment that connected a local `llama3.1:8b`
model to a PentestGPT-style coding workflow. The connection worked; the code
generation did not meet a publishable standard. This page records the negative
results because they are more useful than pretending the first output worked.

## Evidence inspected

- A JSONL request/response trace containing 10 local-model requests and 10
  responses.
- The complete pasted Code Mode transcript.
- The generated detector workspaces and their tests, fixtures, reports, and
  schemas.
- The final package behavior, built distributions, and CI results.

Raw traces are intentionally not committed. Security prompts, local paths, and
machine-specific context can disclose more than a reusable fixture pack should.

## What failed

| Failure | Why it matters | Publication decision |
|---|---|---|
| Python blocks contained non-Python `rustylet` declarations | The files could not parse or run | Rewritten from scratch |
| Generated examples referenced undefined functions and variables | The examples could not satisfy their own tests | Excluded |
| CLI usage prose appeared inside source-code blocks | Copying the answer did not create a runnable project | Replaced with an actual `argparse` CLI |
| A claimed offline simulator later imported `psutil`, enumerated live processes, and called process termination | The implementation contradicted its stated boundary | Excluded and guarded against by a regression test |
| An offline trial workspace later gained a Windows live-memory collector | The workspace no longer matched its own experimental contract | Not included in CrossViewLab |
| Example measurements used hard-coded PIDs, timestamps, hashes, and latency values | Fabricated measurements are not experimental evidence | Replaced with synthetic fixture IDs or omitted |
| Comments were embedded in nominal JSON | The examples were invalid JSON | Replaced with strict JSON fixtures and schema validation |
| The model sometimes refused a safe fixture request and sometimes returned unsafe live-host behavior | Prompt wording was not a reliable control boundary | The boundary is enforced in code and tests |

## What survived review

Four ideas were coherent enough to retain:

1. Compare two independently labeled process-inventory artifacts by PID.
2. Compare shared fields only when both exporters provide them.
3. Compare supplied function-entry bytes with a supplied baseline and triage a
   small set of entry prefixes.
4. Emit a versioned report and validate it with deterministic tests.

Those ideas were independently implemented in CrossViewLab. No source file was
copied from the generated transcript.

## Reproduction evidence

| Check | Result |
|---|---|
| Unit and behavior tests | 19 passed |
| Python versions in CI | 3.10, 3.11, 3.12, 3.13 |
| Runtime dependencies | 0 |
| Demo fixture findings | 6 |
| JSON report schema | Validated in tests |
| Output formats | JSON, Markdown, SARIF |
| Live collection imports in package | 0 |
| Windows process-memory API tokens in package | 0 |

The demo's six findings are not measurements from a real endpoint. They are the
deterministic expected result of the public synthetic fixtures.

## Checklist for reviewing generated security code

Before using model-generated security code in a report or repository:

1. **Parse every file.** Mixed languages and prose inside code blocks are common
   generation failures.
2. **Resolve every symbol.** Search for undefined functions, imports, fixtures,
   variables, and CLI entry points.
3. **Trace the data boundary.** Compare the claimed scope with actual imports and
   calls. An "offline" label is meaningless if the code reads the host.
4. **Separate fixtures from measurements.** Synthetic PIDs and hashes must be
   labeled as fixtures; real measurements require a completed run and provenance.
5. **Test the clean case.** A detector that only sees intentionally anomalous
   fixtures has not demonstrated acceptable false-positive behavior.
6. **Test malformed inputs.** Silent hex repair, duplicate identifiers, and loose
   JSON parsing can turn bad evidence into confident findings.
7. **Treat indicators as triage.** A byte prefix or cross-view mismatch is not
   proof of compromise without corroborating evidence.
8. **Enforce boundaries mechanically.** Tests should fail if prohibited imports
   or platform APIs enter the package.
9. **Run the documented command in a clean environment.** A plausible README is
   not evidence that packaging or entry points work.
10. **Publish the failure record.** Explain what was discarded so readers can
    distinguish verified behavior from generated suggestion.

## Bottom line

The local model was useful for generating candidate structure, but it was not a
reliable coder or experimental witness in this run. CrossViewLab's public claims
come from executable tests, schema validation, package builds, and CI—not from
the model's confidence or prose.
