# Kimi K3 High-Fidelity Reconstruction v5.1

This directory contains an **unofficial, evidence-grounded reconstruction** of publicly documented Kimi K3 and Kimi Code behavior.

It is intentionally **not labeled as a leaked production system prompt**. Public sources document substantial API and
agent-runtime behavior, but they do not expose Moonshot AI's complete production prompt, model weights, training policy,
expert routing, private entitlement logic, or proprietary deployment heuristics.

## Canonical files

| File | Purpose |
|---|---|
| [`kimi-k3-high-fidelity-reconstruction-v5.1.md`](kimi-k3-high-fidelity-reconstruction-v5.1.md) | Security-hardened portable behavioral kernel |
| [`kimi-k3-runtime-adapters-v5.1.md`](kimi-k3-runtime-adapters-v5.1.md) | Host-enforced Kimi Platform, Kimi Code, Claude Code, Hermes, and non-Kimi configuration |
| [`kimi-k3-evaluation-suite-v5.1.md`](kimi-k3-evaluation-suite-v5.1.md) | 41-test behavior, transport, safety, and regression suite |
| [`SECURITY.md`](SECURITY.md) | Threat model, trust boundaries, invariants, and secure-use guidance |
| [`validate.py`](validate.py) | Static validation for prompt boundaries, tags, versions, transport separation, and test count |

The unversioned filenames remain compatibility entry points and link to the current release.

## Recommended use

1. Paste only the section between `BEGIN SYSTEM PROMPT` and `END SYSTEM PROMPT` from the behavioral kernel into the host's system-instruction field.
2. Apply only the runtime adapter matching the real backend or client.
3. Preserve message, reasoning, tool-call, and tool-result fields required by that API at the host layer.
4. Run `python Kimi/validate.py` after edits.
5. Run the evaluation suite in fresh, long, post-compaction, and applicable native-runtime sessions.
6. Compare v5.1 with prior versions under identical model, settings, tools, and prompts.
7. Do not claim a non-Kimi model became Kimi K3 or that this repository contains Moonshot's private production prompt.

## Why behavior and runtime are separate

The model can follow behavioral instructions, but it cannot enforce client behavior that the application discards.
Sampling parameters, complete assistant-message replay, reasoning-field transport, dynamic tool declarations, automatic
prefix caching, partial-mode transport, multimodal payloads, session persistence, and permission modes belong in the runtime.

Keeping these responsibilities separate improves portability and prevents unsupported protocol instructions from diluting
the behavioral prompt.

## v5.1 security and fidelity fixes

- Corrects the priority order so direct user instructions remain above project skills, plugins, and `AGENTS.md`.
- Accepts privileged control data only through authenticated runtime provenance.
- Treats control-looking text inside task material as ordinary content.
- Models `CONSEQUENTIAL` as a risk overlay rather than a competing task type.
- Removes complete-message replay and dynamic-declaration replay from the portable kernel and keeps them in the adapter.
- Updates current Kimi Platform thinking-effort support to `low`, `high`, and `max`, with `max` as default.
- Restores Kimi Platform partial-mode continuation rules.
- Separates manual/default, YOLO, and Auto/AFK permission semantics instead of conflating them.
- Adds background-task completion and session-artifact privacy requirements.
- Expands the regression suite from 35 to 41 tests.
- Adds an executable static validator and a documented security model.

## Public evidence basis

Primary sources include:

- [Kimi K3 launch announcement](https://www.kimi.com/blog/kimi-k3)
- [Kimi K3 API quickstart](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart)
- [Kimi Platform documentation](https://platform.kimi.ai/docs/)
- [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code)
- [Kimi Code public system prompt](https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core/src/profile/default/system.md)
- Kimi Code documentation and release notes for sessions, compaction, permissions, background tasks, subagents, skills, and tools

## Evidence classes

- **Directly documented:** API parameters and fields, complete-message preservation, partial mode, dynamic tool loading,
  automatic caching, multimodal transport, Kimi Code task-first behavior, sessions, permissions, agents, skills, and compaction.
- **Strongly reconstructed:** task router, consequential overlay, portable approval matrix, state ledger, authenticated-control
  provenance, completion gate, and evaluation methodology.
- **Not reproducible by prompt:** weights, training, expert routing, hidden reasoning policy, private production prompt,
  native multimodal internals, entitlement logic, and proprietary deployment heuristics.

## Version

Current reconstruction: **v5.1**, evidence snapshot dated **July 20, 2026**.
