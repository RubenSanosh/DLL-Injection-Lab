# Detecting DLL-injection telemetry

DLL Injection Lab models the observable sequence commonly associated with DLL
injection as synthetic events. It does not implement the mechanism that produces
those events on Windows.

## ATT&CK mapping

The classic scenario maps to MITRE ATT&CK sub-technique **T1055.001: Dynamic-link
Library Injection**. The mapping describes the behavior being studied; it does
not mean the simulator performs the technique.

## Five correlated signals

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

## Benign-lookalike tuning matrix

| Synthetic action | Common benign explanation | Useful enrichment fields | Analyst verification question | Why no standalone alert |
| :--- | :--- | :--- | :--- | :--- |
| Cross-process handle | Debuggers, endpoint agents, or administrative tools requesting access. | signer, path, user, integrity level | Is the source binary an approved administrative or security tool? | Cross-process access is common in legitimate software. |
| Remote memory allocation | Instrumentation, accessibility software, or endpoint products reserving memory in another process. | signer, path, parentage, prevalence | Is this actor-target pair expected in the environment? | Allocation does not establish what content or execution followed. |
| Remote memory write | Debuggers, profilers, or approved instrumentation modifying a target process. | signer, path, user, actor-target prevalence | Did the same approved tool request the handle and allocation? | A write is ambiguous without content, target, and sequence context. |
| Remote thread start | Debuggers, profilers, installers, or security products starting work in another process. | signer, path, user, integrity level, parentage | Is cross-process execution expected for this signed actor and target? | Legitimate tools can create remote threads during normal operation. |
| Module image load | Approved plug-ins, extensions, or application components loading into a process. | signer, path, hash prevalence, user, acquisition quality | Is the module trusted, expected, and loaded from an approved path? | Image loads are routine and require the preceding actor-target chain for context. |

## Correlation contract

A finding requires all five actions in order within the same `flow_id`. Every
matched event must keep the same actor PID, target PID, and module, and the actor
and target PIDs must differ. Correlation sorts supplied records by the synthetic
event-time `tick`, so delayed JSONL arrival does not break an otherwise complete
sequence. Extra or duplicate events may occur between required actions, but missing,
event-time-reordered, or inconsistent required actions prevent the finding.

This contract makes three important tests straightforward:

- Remove one event and confirm the finding disappears.
- Change the flow ID of one event and confirm correlation breaks.
- Set actor and target to the same PID and confirm the clean control stays clean.

The CLI exposes those delivery cases without manual fixture editing:

```bash
dll-injection-lab demo --variant missing-thread
dll-injection-lab demo --variant out-of-order-arrival
dll-injection-lab demo --variant duplicate-write
```

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
