# Detecting DLL-injection telemetry

DLL Injection Lab models the observable sequence commonly associated with DLL
injection as synthetic events. It does not implement the mechanism that produces
those events on Windows.

## ATT&CK mapping

The classic scenario maps to MITRE ATT&CK sub-technique **T1055.001: Dynamic-link
Library Injection**. The mapping describes the behavior being studied; it does
not mean the simulator performs the technique.

## Five correlated signals

## Benign-lookalike Tuning Matrix

| Synthetic Action | Common Benign Explanation | Useful Enrichment Fields | Analyst Verification Question | Why No Standalone Alert |
| :--- | :--- | :--- | :--- | :--- |
| Cross-process handle | Debuggers, endpoint agents, or administrative tools requesting access. | signer, path, user, integrity level | Is the source binary a signed administrative/security tool? | Too common in normal OS/software operations to alert on alone. |
| Remote memory allocation | Valid inter-process communications or legitimate monitoring apps. | parentage, prevalence, acquisition quality | Does the targeting process regularly allocate memory in peer processes? | Creates high false-positive rates if flagged independently. |
| Remote thread context write | Legitimate thread manipulation by OS utilities or crash reporting tools. | signer, path, parentage | Is this execution part of an expected application framework task? | Context switching and thread writes happen natively in many frameworks. |
| Remote thread execution | System diagnostics, profilers, or routine sub-routine execution. | user, path, prevalence | Was the target thread spawned by an authenticated system service? | Generating alerts here without context swamps analysts with noise. |
| Unbacked memory execution | Dynamic JIT compilers or runtime script environments. | acquisition quality, integrity level, signer | Is the target process running a JIT engine (e.g., V8, .NET)? | JIT engines naturally execute unbacked memory blocks during standard runtime. |
### 1. Cross-process handle

One fictional process requests access to a different fictional process. This is
useful context but too common to alert on by itself. Debuggers, accessibility
tools, endpoint products, and administrative utilities can create similar
telemetry.

### 2. Remote memory allocation

The same correlation flow records a remote memory reservation. Allocation alone
is still ambiguous and should be joined with actor, target, timing, and later
events.

### 3. Remote memory write

The actor stages a fictional module path in the synthetic target region. The lab
records only a description and URI; it never allocates or writes memory.

### 4. Remote thread start

The synthetic flow records a cross-process execution signal. This materially
raises confidence when it follows the first three observations.

### 5. Module image load

The fictional target records the expected synthetic module. Joining the module
load to the preceding actor-target flow completes the built-in correlation.

## Correlation contract

A finding requires all five actions in order within the same `flow_id`. Every
matched event must keep the same actor PID, target PID, and module, and the actor
and target PIDs must differ. Extra events may occur between required actions, but
missing, reordered, or inconsistent required actions prevent the finding.

This contract makes three important tests straightforward:

- Remove one event and confirm the finding disappears.
- Change the flow ID of one event and confirm correlation breaks.
- Set actor and target to the same PID and confirm the clean control stays clean.

## Clean control

The `cooperative` scenario models an explicitly approved plug-in load inside the
fictional host's own process. It emits `user_approval`,
`self_module_load_requested`, and `image_load`. Because no cross-process chain
exists, the detector returns zero findings.

## Triage, not proof

Even a real five-signal sequence would require corroboration. Security products,
debuggers, installers, accessibility software, and controlled testing tools can
produce injection-like activity. A production rule should incorporate signer,
path, user, integrity level, parentage, prevalence, allowlists, and acquisition
quality.

DLL Injection Lab deliberately stops at portable correlation logic. Acquisition
and enforcement belong to separately authorized endpoint workflows.
