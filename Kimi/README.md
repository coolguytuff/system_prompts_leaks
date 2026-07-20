# Kimi K3 High-Fidelity Reconstruction v6.0

This directory contains an **unofficial, evidence-grounded reconstruction** of publicly documented Kimi K3 and Kimi Code
behavior. It is not Moonshot AI's private production prompt and cannot reproduce K3's weights, training, expert routing, or
proprietary inference stack.

## Canonical files

| File | Purpose |
|---|---|
| [`kimi-k3-high-fidelity-reconstruction-v6.0.md`](kimi-k3-high-fidelity-reconstruction-v6.0.md) | Portable behavioral system-prompt kernel |
| [`kimi-k3-runtime-adapters-v6.0.md`](kimi-k3-runtime-adapters-v6.0.md) | Host-enforced API, client, retry, caching, tool, multimodal, and Kimi Code guidance |
| [`kimi-k3-evaluation-suite-v6.0.md`](kimi-k3-evaluation-suite-v6.0.md) | 58-test behavior, transport, safety, and regression suite |
| [`kimi-k3-evidence-v6.0.md`](kimi-k3-evidence-v6.0.md) | Evidence matrix, source scope, conflicts, and reconstruction decisions |
| [`kimi-k3-v6.0-audit.md`](kimi-k3-v6.0-audit.md) | Comprehensive findings and remediation record |
| [`SECURITY.md`](SECURITY.md) | Threat model, trust boundaries, invariants, and deployment checklist |
| [`validate.py`](validate.py) | Deterministic package and repository validator |

The unversioned filenames remain compatibility entry points and link to the current release.

## Recommended deployment

1. Paste only the section between `BEGIN SYSTEM PROMPT` and `END SYSTEM PROMPT` from the behavioral kernel into the host's
   system-instruction field.
2. Apply only the runtime adapter matching the actual model, endpoint, client, and product version.
3. Preserve all message, reasoning, call-ID, dynamic-tool, Partial Mode, and result fields required by the selected API.
4. Implement transaction receipts and idempotency for side-effecting tools.
5. Use least-privilege workspace, connector, network, and permission controls.
6. Run `python Kimi/validate.py` after every package edit.
7. Run critical evaluation tests in fresh, long, interrupted, resumed, and post-compaction sessions.
8. Compare v6.0 with v5.1 under identical model, settings, tools, and prompts.
9. Do not claim that a non-Kimi model became Kimi K3 or that this repository contains Moonshot's private prompt.

## Why behavior and runtime are separate

A model can follow behavioral instructions, but it cannot enforce client behavior that the application discards. Sampling,
complete assistant-message replay, reasoning fields, dynamic declarations, cache hints, Partial Mode, retries, multimodal
payloads, goal/session persistence, permission modes, hooks, and idempotency belong in the runtime.

Keeping transport outside the behavioral kernel improves instruction salience and prevents non-Kimi hosts from imitating
unsupported protocol fields.

## v6.0 highlights

- Adds proof-based long-horizon goal state: ACTIVE, COMPLETE, PAUSED, and BLOCKED.
- Adds explicit REQUESTED / REQUIRED / ADJACENT RISK / OPTIONAL scope control to counter excessive proactivity.
- Adds tool transaction receipts, duplicate-call protection, unknown-outcome reconciliation, and interrupted-call closure.
- Resolves K3-specific versus generic `tool_choice="required"` documentation without overgeneralizing.
- Separates automatic prefix caching from optional `prompt_cache_key` session hints.
- Adds status-aware retry/reconnect guidance with bounded jitter and non-idempotent safety.
- Adds current image/video formats, resolution recommendations, body limits, token estimation, and upload deletion.
- Adds SSRF and redirect-chain protections for URL retrieval.
- Adds native Kimi Code goal queues, compaction hints, fork isolation, live permission propagation, and fail-open hook rules.
- Expands regression coverage from 41 to 58 tests.
- Adds a source/conflict evidence matrix and comprehensive audit report.
- Strengthens static validation against bloat, duplicated directives, missing contracts, stale links, and CI weakening.

## Public evidence basis

Primary sources are catalogued in [`kimi-k3-evidence-v6.0.md`](kimi-k3-evidence-v6.0.md), including K3-specific API
pages, the K3 launch material, the public Kimi Code system prompt, goals, sessions, hooks, interaction documentation, and
current changelog.

## Truth boundary

**Directly documented:** K3 API parameters and limits, complete-message preservation, K3-specific Tool Choice, dynamic tools,
automatic caching, Partial Mode, multimodal transport, Kimi Code action posture, sessions, goals, modes, hooks, skills,
compaction, and subagents.

**Strongly reconstructed:** task router, scope classifier, consequential overlay, host-independent goal contract, claim and
transaction ledgers, authenticated-control provenance, completion gate, and cross-host fallback behavior.

**Not reproducible by prompt:** model weights, training, learned representations, expert routing, hidden reasoning policy,
native multimodal internals, private production prompts, entitlement logic, and proprietary deployment heuristics.

## Version

Current reconstruction: **v6.0**, evidence snapshot dated **July 20, 2026**.
