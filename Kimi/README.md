# Kimi K3

This directory contains an **unofficial, evidence-grounded high-fidelity reconstruction** of Kimi K3 and Kimi Code behavior.

It is intentionally **not labeled as a leaked production system prompt**. Public sources document a large amount of K3's API and agent-runtime behavior, but they do not expose Moonshot AI's complete production prompt, model weights, training policy, expert routing, private entitlement logic, or proprietary deployment heuristics.

## Files

| File | Purpose |
|---|---|
| [`kimi-k3-high-fidelity-reconstruction.md`](kimi-k3-high-fidelity-reconstruction.md) | Portable behavioral system-prompt kernel for Kimi and non-Kimi hosts |
| [`kimi-k3-runtime-adapters.md`](kimi-k3-runtime-adapters.md) | Host-enforced configuration for Kimi Platform, Kimi Code, Claude Code, Hermes, and non-Kimi hosts |
| [`kimi-k3-evaluation-suite.md`](kimi-k3-evaluation-suite.md) | 35-test regression suite for behavior, tools, context, multimodality, safety, and completion |

## Recommended use

1. Paste only the section between `BEGIN SYSTEM PROMPT` and `END SYSTEM PROMPT` from the behavioral reconstruction into the host's system-instruction field.
2. Apply only the runtime adapter matching the real backend or client.
3. Preserve all message, reasoning, tool-call, and tool-result fields required by the selected API.
4. Run the evaluation suite in fresh, long, and post-compaction sessions.
5. Do not claim that a non-Kimi model has become Kimi K3 or that this repository contains Moonshot's private production prompt.

## Why the project is split

A prompt can shape observable behavior, but it cannot enforce transport behavior that the client discards. Sampling parameters, automatic prefix caching, complete assistant-message replay, dynamic tool declarations, multimodal payload formats, session persistence, and approval modes belong in the runtime or client layer.

Keeping these responsibilities separate improves portability and prevents non-Kimi hosts from being distracted by protocol instructions they cannot execute.

## Public evidence basis

Primary public sources used for the reconstruction include:

- [Kimi K3 launch announcement](https://www.kimi.com/blog/kimi-k3)
- [Kimi K3 API quickstart](https://platform.moonshot.ai/docs/guide/kimi-k3-quickstart)
- [Kimi Platform documentation](https://platform.moonshot.ai/docs/)
- [MoonshotAI/kimi-code](https://github.com/MoonshotAI/kimi-code)
- [Kimi Code public system prompt](https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core/src/profile/default/system.md)

The reconstruction also uses public Kimi Code documentation and release notes for sessions, compaction, approvals, subagents, skills, and tool behavior.

## Evidence classes

- **Directly documented:** K3 API fields and fixed parameters, full-message preservation, dynamic tool loading, automatic caching, multimodal input, Kimi Code sessions, approval modes, built-in agent roles, and public Kimi Code prompt behavior.
- **Strongly reconstructed:** the task router, portable approval matrix, task-state ledger, compaction checklist, host-independent completion gates, and evaluation methodology.
- **Not reproducible by prompt:** model weights, training, expert routing, hidden reasoning policy, native multimodal internals, private system prompts, entitlement logic, and proprietary production heuristics.

## Version

Current reconstruction: **v5.0**, evidence snapshot dated **July 20, 2026**.
