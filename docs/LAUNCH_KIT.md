# Launch kit

Copy, adapt, and post these messages when announcing DLL Injection Lab. Do not
claim that it performs real DLL injection; the safe synthetic boundary is the
product advantage.

## One-line pitch

Learn how defenders detect DLL injection by simulating the full telemetry chain—
without injecting a DLL or touching a live process.

## Short social post

I built DLL Injection Lab 🧪

It generates a deterministic five-event DLL-injection telemetry chain, detects
the correlated sequence, and includes a clean cooperative-load control.

No VM. No admin. No malware. Zero live processes touched. JSONL, Markdown, JSON,
and SARIF included.

Try it in 60 seconds: https://github.com/bsmensah-ctrl/DLL-Injection-Lab

If it saves you lab setup time, a ⭐ helps other defenders find it.

## LinkedIn post

DLL-injection labs usually make students choose between running offensive code
in a VM or reading slides without testing a detector. I wanted a safer third
option.

DLL Injection Lab emits the complete synthetic telemetry sequence—cross-process
handle, remote allocation, remote write, remote thread, and module load—then
correlates it into an explainable ATT&CK T1055.001 finding. It also includes a
same-process cooperative plug-in load as a clean control.

The project has zero runtime dependencies, 30 tests, Python 3.10–3.13 CI, and
JSON, Markdown, and SARIF output. It never calls a Windows process-memory API.

Repository: https://github.com/bsmensah-ctrl/DLL-Injection-Lab

Feedback from SOC analysts, instructors, and detection engineers is welcome.

## Reddit post

**Title:** I built a zero-risk DLL-injection detection lab: full telemetry chain,
no live process access

**Body:** I wanted a way to teach and test multi-event DLL-injection detection
without requiring students to run an injector. This project generates a fully
synthetic five-event sequence, correlates it to ATT&CK T1055.001, and includes a
cooperative same-process load as a clean control. You can delete or reorder JSONL
events to see exactly when the detection fails. Zero runtime dependencies and 30
tests. I would especially value feedback on the event contract and future safe
scenarios: https://github.com/bsmensah-ctrl/DLL-Injection-Lab

## Hacker News / Show HN

**Title:** Show HN: DLL Injection Lab – detect a synthetic injection chain without
touching a live process

**Text:** DLL Injection Lab generates deterministic JSONL telemetry for the five
signals in a classic DLL-injection chain, correlates them into an explainable
finding, and provides a clean same-process control. It is intentionally not an
injector: no Windows APIs, admin rights, VM, or runtime dependencies. I built it
after a local LLM prototype failed its own offline boundary. Feedback on the
detection contract and teaching workflow is welcome.

## Suggested screenshots

1. The repository social preview.
2. `dll-injection-lab demo` returning one high finding.
3. `dll-injection-lab demo --scenario cooperative` returning zero findings.
4. The five-stage Mermaid diagram from the README.
