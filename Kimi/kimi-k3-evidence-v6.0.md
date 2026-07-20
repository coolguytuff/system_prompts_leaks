# Kimi K3 Reconstruction Evidence Matrix v6.0

Evidence snapshot: **July 20, 2026**.
Kimi Code source snapshot commit: **`c2d7bebd04106473bb4dbab2903756aa3f14a880`**.

This document separates directly documented behavior from reconstruction decisions and records how conflicting public
documentation was resolved. Re-check every mutable claim before a later release.

## Evidence classes

- **DIRECT** — stated in current first-party Kimi or Moonshot documentation/source.
- **SOURCE-INFERRED** — strongly inferred from multiple first-party behaviors or release changes.
- **RECONSTRUCTED** — portable design added to reproduce the observed behavior across hosts.
- **HOST-REQUIRED** — cannot be enforced by the model prompt and must be implemented by the client/runtime.
- **UNREPRODUCIBLE** — model weights, training, internal routing, or private production behavior unavailable publicly.

## Primary sources

1. Kimi K3 launch and technical overview: <https://www.kimi.com/blog/kimi-k3>
2. Kimi K3 API quickstart: <https://platform.kimi.ai/docs/guide/kimi-k3-quickstart>
3. Thinking effort: <https://platform.kimi.ai/docs/guide/use-thinking-effort>
4. Vision input: <https://platform.kimi.ai/docs/guide/use-kimi-vision-model>
5. Partial Mode: <https://platform.kimi.ai/docs/api/partial>
6. Dynamic tools: <https://platform.kimi.ai/docs/guide/use-dynamic-tool-loading>
7. Tool choice: <https://platform.kimi.ai/docs/guide/use-tool-choice>
8. Tool calling best practices: <https://platform.kimi.ai/docs/guide/tool-calling-best-practice>
9. Chat Completions reference: <https://platform.kimi.ai/docs/api/chat>
10. API errors: <https://platform.kimi.ai/docs/api/errors>
11. Kimi Code source snapshot: <https://github.com/MoonshotAI/kimi-code/tree/c2d7bebd04106473bb4dbab2903756aa3f14a880>
12. Current Kimi Code system prompt:
    <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/packages/agent-core-v2/src/app/agentProfileCatalog/system.md>
13. Kimi Code interaction guide: <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/docs/en/guides/interaction.md>
14. Kimi Code sessions guide: <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/docs/en/guides/sessions.md>
15. Kimi Code goals guide: <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/docs/en/guides/goals.md>
16. Kimi Code hooks guide: <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/docs/en/customization/hooks.md>
17. Kimi Code changelog: <https://github.com/MoonshotAI/kimi-code/blob/c2d7bebd04106473bb4dbab2903756aa3f14a880/apps/kimi-code/CHANGELOG.md>

## Model and architecture

| Claim | Class | Evidence and implementation consequence |
|---|---|---|
| K3 has 2.8T parameters, KDA, Attention Residuals, native visual understanding, and a 1M context window. | DIRECT | K3 launch and quickstart. Descriptive only; no prompt can reproduce architecture. |
| K3 activates 16 of 896 experts and is reported as roughly 2.5× more scaling-efficient than K2. | DIRECT vendor claim | Kept in research notes, not encoded as behavioral instruction. |
| K3 is designed for long-horizon coding, knowledge work, reasoning, and vision-in-the-loop workflows. | DIRECT | Kernel emphasizes sustained execution, evidence, visual feedback, and verified completion. |
| K3's full weights were scheduled for July 27, 2026, with more technical details to follow. | DIRECT and time-sensitive | Re-check after that date; v6 does not claim details not yet public at this snapshot. |

## Behavioral signature

| Behavior | Class | Source and implementation |
|---|---|---|
| Treat ambiguous question-versus-action requests as tasks when access exists. | DIRECT | Public Kimi Code system prompt; encoded in task router and operating posture. |
| Use actual tools for requested file/code changes. | DIRECT | Public Kimi Code prompt; encoded in ACT mode. |
| Prefer dedicated Read/Glob/Grep-style capabilities over raw shell. | DIRECT | Public Kimi Code prompt; generalized to scoped tools. |
| Parallelize independent reads but serialize dependent writes. | DIRECT | Public prompt; encoded in tool policy. |
| Use sparse phase updates rather than narrating every tool call. | DIRECT | Public prompt; encoded in communication. |
| Minimal code changes, dependency verification, local conventions, and real testing. | DIRECT | Public prompt; encoded in coding module. |
| Long autonomous work should have a finish line and evidence. | DIRECT | Kimi Code goals guide; encoded as host-independent goal contract. |
| Excessive proactivity is a known K3 limitation. | DIRECT | K3 launch limitations; encoded as scope classification and bounded autonomy. |

## K3 API contract

| Claim | Class | Resolution |
|---|---|---|
| `reasoning_effort` supports `low`, `high`, and `max`; default is `max`. | DIRECT, K3-specific | Runtime adapter uses `max` for maximum fidelity. |
| K3 always thinks and requires complete assistant-message replay. | DIRECT | Host must preserve full assistant objects, not only visible content. |
| Hosted sampling is fixed at temperature 1.0 and top-p 0.95. | DIRECT | Omit overrides in production. |
| Launch benchmark used top-p 1.0. | DIRECT benchmark detail | Kept separate from hosted production settings. |
| K3 `tool_choice="required"` is supported for an initial mandatory call. | DIRECT, K3-specific | K3 quickstart takes precedence for `kimi-k3`. |
| Generic migration docs say `required` is unsupported. | DIRECT but broader/older scope | Do not generalize K3 support to other models or gateways. Model-specific docs win for K3. |
| Top-level tools are limited to 128. | DIRECT API reference | Runtime validates and uses dynamic loading for larger registries. |
| Dynamic tools are complete system-message declarations, effective from their position and replayed later. | DIRECT | Host-enforced dynamic registry protocol. |
| Automatic prefix caching requires no manual cache ID or TTL. | DIRECT, K3-specific | Keep stable prefixes byte-for-byte stable. |
| `prompt_cache_key` is also available as an agent/session hint. | DIRECT API reference | Optional stable opaque key; not a replacement for automatic caching. |
| Partial Mode appends an assistant prefix with `partial=true`. | DIRECT | Returned content is suffix; prefix prepended once. |
| Partial Mode should not be mixed with `response_format=json_object`. | DIRECT | Runtime rejects the combination. |
| Strict JSON Schema applies to final `message.content`, not reasoning content. | DIRECT | Application parses and validates only final content. |

## Multimodal contract

| Claim | Class | Implementation |
|---|---|---|
| K3 supports native image and video input. | DIRECT | Typed `image_url`/`video_url` blocks. |
| Public image URLs are unsupported; use base64 or `ms://` uploaded-file references. | DIRECT | Adapter rejects unsupported URL transport. |
| Images: png/jpeg/webp/gif; videos include mp4/mpeg/mov/avi/x-flv/mpg/webm/wmv/3gpp. | DIRECT | Adapter lists current formats. |
| Recommended image ≤4096×2160 and video ≤1920×1080. | DIRECT | Preprocess larger media unless detail requirements justify otherwise. |
| Vision request body must remain within 100 MB. | DIRECT | Validate before sending and prefer uploads for large/reused media. |
| Temporary uploaded files should be deleted when no longer needed. | SOURCE-INFERRED from official examples and privacy | Adapter tracks lifecycle and deletion result. |

## Kimi Code runtime

| Behavior | Class | Implementation |
|---|---|---|
| Manual, YOLO, Auto, and Plan modes have distinct semantics. | DIRECT | Adapter does not collapse modes. |
| YOLO permits questions and still protects sensitive access/Plan exit; Auto is unattended. | DIRECT | Explicit mode matrix. |
| Running subagents should observe later permission-mode changes. | DIRECT changelog | Adapter requires live permission propagation. |
| Compaction preserves retained user messages, a first-person summary, exact outcomes, and TODO state. | DIRECT | Kernel state ledger and refresh rules. |
| Goals transition among active, complete, paused, and blocked. | DIRECT | Goal contract mirrors lifecycle. |
| Queued goals do not influence the active goal and do not advance after pause/block/cancel. | DIRECT | Goal queue isolation rule. |
| Hooks fail open on script error/timeout and are not sufficient as a sole security barrier. | DIRECT | Security model and adapter require independent permission controls. |
| Session exports can contain prompts, paths, schemas, command output, and logs. | DIRECT | Redaction and no-raw-session-publication rules. |
| Interrupted model responses can leave tool calls needing explicit closure. | DIRECT changelog | Adapter preserves call IDs and records interruption without fake execution. |

## Reconstructed mechanisms

These are not claimed as Moonshot's private prompt text. They are portable mechanisms chosen to reproduce documented outcomes:

- five-mode task router plus CONSEQUENTIAL risk overlay;
- REQUESTED / REQUIRED / ADJACENT RISK / OPTIONAL scope classifier;
- host-independent goal contract with proof, budget, status, and next action;
- compact claim ledger for research;
- tool transaction ledger and idempotency reconciliation;
- completion and saturation gates;
- authenticated-control provenance rule;
- cross-host multimodal fallback honesty;
- subagent context-minimization and permission-refresh rules.

## Security additions beyond model behavior

These are defense-in-depth requirements for production harnesses, not claims about K3 internals:

- retry classification and bounded exponential backoff;
- side-effect idempotency and unknown-outcome reconciliation;
- SSRF protection across DNS and redirects;
- uploaded-file retention and deletion controls;
- non-secret `prompt_cache_key` design;
- hook fail-open awareness;
- CI action pinning and least-privilege credentials.

## Conflict-resolution policy

When first-party sources conflict:

1. Prefer documentation specific to `kimi-k3` over generic Kimi migration guidance.
2. Prefer the current API reference for request fields and limits.
3. Prefer current source and changelog for Kimi Code runtime behavior.
4. Distinguish product surfaces: Kimi Platform, Kimi Code, Kimi CLI legacy docs, and third-party gateways.
5. Preserve the conflict in this matrix rather than silently selecting a universal claim.
6. Re-test behavior against the actual endpoint before production deployment.

## Known limits

No public prompt reconstruction can reproduce:

- model weights or learned representations;
- expert routing and inference scheduling;
- training data, post-training, or hidden reward policies;
- native multimodal encoders;
- private system prompts, entitlement logic, or production heuristics;
- host capabilities that are not exposed to the model.

The strongest emulation therefore combines the behavioral kernel, correct runtime adapter, real tools, preserved history,
multimodal transport, permissions, and empirical evaluation.
