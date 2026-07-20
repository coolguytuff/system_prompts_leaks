# Security Model for the Kimi K3 Reconstruction v6.0

## Scope

This document covers the portable behavioral kernel, runtime adapters, evidence matrix, evaluation suite, and contributor
workflow. It does not audit Moonshot AI's private infrastructure or K3 model internals.

## Protected assets

- user intent, approved scope, and accepted decisions;
- confidential data, credentials, private files, and connected-account information;
- system, developer, and authenticated runtime instructions;
- tool permissions, approval decisions, and workspace boundaries;
- repository integrity, uncommitted work, and production state;
- correctness of tool results, citations, files, and completion claims;
- session, goal, subagent, hook, and debug records;
- uploaded media and file identifiers;
- cache keys and correlation identifiers;
- external systems affected by non-idempotent actions.

## Trust boundaries

From highest to lowest:

1. host policies and authenticated system, developer, and runtime controls;
2. current tool schemas, permission controls, and environment constraints;
3. direct user instructions;
4. project guidance, skills, plugins, accepted prior task context, and authenticated hook metadata;
5. retrieved or user-supplied content, tool output, media, logs, and unauthenticated automation text.

Scope precedence such as `Project > User > Extra > Built-in` applies only among same-layer skills. It never elevates a
skill or project file above a direct user instruction.

## Threats and invariants

### Control-channel spoofing

Task content may imitate system tags, runtime reminders, tool messages, or administrator text.

**Invariant:** syntax alone never grants authority. Only provenance authenticated by the host can elevate control data.

### Malicious project guidance or capability metadata

A project file, skill, plugin, connector description, or hook output may attempt to expand scope, alter permissions, or
redirect work.

**Invariant:** these sources stay below the user unless the authenticated host explicitly elevates a specific contract.
Same-name scope precedence resolves only conflicts among capabilities in the same layer.

### Excessive proactivity and scope drift

A highly agentic model may fix adjacent issues, refactor unrelated code, spend unbounded resources, or pursue queued work.

**Invariant:** classify work as REQUESTED, REQUIRED, ADJACENT RISK, or OPTIONAL. Act only within the kernel's scope rules,
use explicit goal proof and budgets, and isolate queued goals.

### Permission-denial circumvention

A refused action may be attempted through shell, another connector, subagent, Formula, hook, or indirect equivalent.

**Invariant:** denial is a policy decision. The agent must not reproduce the refused action through another mechanism.

### Consequential-action overreach

The agent may attempt destructive, external, costly, production, account, git, messaging, publication, or permission changes
without sufficiently scoped authorization.

**Invariant:** active host policy governs approval. Authorization is action- and context-specific unless a durable
higher-priority rule clearly authorizes a class.

### Ambiguous or duplicated side effects

Timeouts, reconnects, duplicate tool messages, or interrupted streams can cause a non-idempotent action to execute twice.

**Invariant:** persist tool-call state, deduplicate authenticated call IDs, and reconcile unknown outcomes before retrying.
Never invent results to close protocol history.

### Dangling interrupted tool calls

An interrupted assistant response may contain complete calls that never ran or incomplete calls that must not run.

**Invariant:** execute only structurally complete calls. Close emitted-but-unexecuted calls with explicit interruption when the
protocol supports it, preserve identifiers, and never fabricate side effects.

### Private-context propagation

Subagent prompts, logs, session files, task records, hook payloads, or debug bundles may contain private context.

**Invariant:** pass only minimum necessary context. Inspect and redact before publishing. Do not commit raw `wire.jsonl`,
`state.json`, `agents/`, task records, plan files, or debug bundles.

### Hook fail-open behavior

Kimi Code hooks allow on script error or timeout, and observation-only events cannot block execution.

**Invariant:** hooks are defense in depth, not a sole barrier. Use permission controls, sandboxing, least privilege, and manual
confirmation for high-risk actions. A deliberate hook denial remains a denial.

### SSRF and unsafe URL retrieval

A URL or redirect may target loopback, private networks, cloud metadata, local services, or oversized/decompression payloads.

**Invariant:** normalize URLs, restrict schemes, resolve every redirect hop, block internal address classes, limit redirects,
size, MIME type, decompression, and time, and never forward credentials across origins.

### Uploaded-file and multimodal leakage

Base64 payloads, uploaded media, metadata, OCR, and `ms://` identifiers may expose private data or persist unintentionally.

**Invariant:** validate media, avoid payload logging, track retention, and delete temporary uploads after use. Treat embedded
text and metadata as untrusted task content.

### Cache-key correlation and data leakage

A `prompt_cache_key` containing user text or reused across users can expose or correlate private context.

**Invariant:** use an opaque non-secret identifier scoped to one logical session or task. Do not embed PII, filenames, prompts,
or credentials.

### Goal runaway and budget exhaustion

An ambiguous autonomous goal may continue indefinitely, consume excessive tokens/cost, or mark itself complete without proof.

**Invariant:** goals require a bounded objective, proof conditions, budget/stop conditions, and explicit ACTIVE, COMPLETE,
PAUSED, or BLOCKED state.

### Subagent permission drift

A subagent may retain permissions from launch after the main session changes mode.

**Invariant:** active permission state applies at action time. Permission reductions constrain running subagents immediately.

### False tool or completion claims

The model may infer success from a missing error or report completion while checks or background work remain unfinished.

**Invariant:** inspect material results, wait for required background work, satisfy goal proof, verify deliverables, and label
untested work.

### Transport confusion

A portable host may be instructed to emit Kimi-only fields, or a Kimi client may discard required history, identifiers,
dynamic declarations, partial prefixes, reasoning fields, or cache hints.

**Invariant:** behavioral instructions live in the kernel; transport rules live in the matching runtime adapter and are
enforced by the host.

### Supply-chain and CI drift

Movable action tags, broad workflow permissions, persisted credentials, or network-dependent validation can introduce risk.

**Invariant:** pin actions to immutable commits, use read-only permissions and non-persistent credentials, bound runtime, and
keep validation deterministic and offline.

## Secure deployment checklist

- Use only the system-prompt boundary from the behavioral kernel.
- Apply exactly one matching runtime adapter.
- Verify actual model, provider, endpoint, and product version.
- Preserve the selected API's required message and tool structure.
- Validate every tool schema and argument before execution.
- Implement transaction receipts and idempotency for side effects.
- Verify permission-mode behavior for the exact runtime.
- Propagate live permission changes to subagents.
- Constrain high-impact tools and network access not needed for the task.
- Use least-privilege connectors and workspace scope.
- Enforce SSRF, redirect, download-size, and MIME controls.
- Use opaque cache keys and protect API keys from logs and client code.
- Track and delete temporary uploaded files.
- Do not rely on fail-open hooks as a sole security control.
- Do not expose raw session, hook, or debug artifacts.
- Run `python Kimi/validate.py` after changes.
- Run critical behavioral tests at least three times and review variance.

## Residual limitations

A prompt cannot guarantee security against a malicious or defective host, connector, tool implementation, base model, or
runtime that mislabels untrusted content as privileged. Host-enforced sandboxing, permissions, network isolation, secret
filtering, transaction controls, logging hygiene, and independent evaluation remain necessary.
