# Security policy

## Supported versions

Security fixes are applied to the latest release on `main`.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting feature on this repository. Do not
open a public issue with exploit details or sensitive fixture data.

Include the affected version, impact, minimal reproduction, and any suggested
mitigation. You should receive an acknowledgment within seven days.

## Scope

CrossViewLab parses untrusted JSON artifacts. Parser crashes, path handling
issues, unsafe output rendering, dependency compromise, and violations of the
offline-only boundary are in scope.
