# Contributing to DLL Injection Lab

DLL Injection Lab welcomes small, testable improvements to synthetic scenarios,
detection logic, artifact parsing, report formats, documentation, and fixture packs.

## Ground rules

- Keep the package offline and deterministic.
- Do not add host enumeration, process access, memory reads, registry access,
  service control, drivers, network clients, injection, hooking, or evasion.
- Treat every finding as a triage signal and document plausible benign causes.
- Use synthetic or fully sanitized fixtures in issues and tests.
- Add an observable-behavior test for every behavior change.

## Local checks

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

Open an issue before a large schema or CLI change so the contract can be agreed
before implementation.
