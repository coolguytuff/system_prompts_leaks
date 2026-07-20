# Kimi K3 Reconstruction v6.0 — Comprehensive Audit and Remediation

Audit date: **July 20, 2026**.

## Audit scope

The review covered:

- the v5.1 behavioral kernel, runtime adapter, evaluation suite, security model, validator, CI, and repository links;
- Kimi K3 launch material and current K3-specific API documentation;
- Kimi Platform request, tool, vision, Partial Mode, caching, and error contracts;
- the current public Kimi Code system prompt, source, interaction/session/goal/hook documentation, and changelog;
- prompt fidelity, instruction priority, long-horizon execution, scope control, security boundaries, transport correctness,
  retry safety, multimodal lifecycle, subagents, and measurable regression coverage.

## Material findings and fixes

### 1. Long-horizon work lacked a formal goal lifecycle

**Finding:** v5.1 had an execution loop and state ledger but no explicit proof-based goal contract. Kimi Code's current goal
system distinguishes active, complete, paused, and blocked states and isolates queued goals.

**Fix:** v6 adds objective, proof, constraints, budgets, stop conditions, state, and next action. Completion requires evidence;
interruptions pause; missing authority or impossibility blocks; queued work cannot expand the active objective.

### 2. Scope control was still too implicit

**Finding:** Moonshot identifies excessive proactivity as a K3 limitation. Minimal-change wording alone did not define how to
handle adjacent defects discovered during work.

**Fix:** v6 classifies work as REQUESTED, REQUIRED, ADJACENT RISK, or OPTIONAL and supplies an explicit action rule based on
correctness, reversibility, blast radius, cost, and user intent.

### 3. Tool retries could duplicate external side effects

**Finding:** v5.1 distinguished technical errors from denials but did not define durable transaction state or unknown-outcome
reconciliation after timeout, disconnect, or duplicate delivery.

**Fix:** v6 adds a transaction ledger keyed by authenticated call ID, state transitions, result receipts, deduplication, and a
rule forbidding blind retries of non-idempotent actions.

### 4. Interrupted model turns could leave invalid tool history

**Finding:** Kimi Code's current changelog records tool calls that never ran and closes them with interrupted results. v5.1
mentioned background tasks but not the interrupted assistant/tool-call boundary.

**Fix:** v6 separates incomplete calls from complete-but-unexecuted calls, preserves IDs, records explicit interruption when
supported, and forbids fabricated tool results.

### 5. K3-specific and generic `tool_choice` documentation conflicts

**Finding:** the current K3 quickstart documents `tool_choice="required"` for `kimi-k3`; generic migration guidance says the
Kimi API does not support it.

**Fix:** v6 records the conflict and applies model-specific precedence: `required` is used only for the current K3 contract,
then returns to `auto`; it is never generalized to older models, compatibility gateways, or third-party providers.

### 6. Automatic caching and `prompt_cache_key` were conflated by omission

**Finding:** K3 automatically caches stable prefixes without a cache ID, while the Chat Completions reference also exposes an
optional stable `prompt_cache_key` for agents and requires it for Kimi Code Plan cache optimization.

**Fix:** v6 distinguishes the two mechanisms, defines stable prefix construction, and requires opaque, non-sensitive,
session-scoped cache keys when used.

### 7. Partial Mode had missing incompatibility and continuation details

**Finding:** v5.1 restored Partial Mode but omitted the documented warning against mixing it with JSON Object mode and did not
fully describe truncated-thinking continuation.

**Fix:** v6 rejects Partial Mode plus `response_format=json_object`, preserves available assistant reasoning fields, treats the
response as suffix only, and prepends the prefix exactly once.

### 8. Multimodal transport lacked complete operational limits

**Finding:** v5.1 covered base64 and `ms://` transport but not current format lists, recommended resolutions, request-body
limit, token estimation, signature validation, logging hygiene, or uploaded-file retention.

**Fix:** v6 adds documented formats, 4K/FHD recommendations, 100 MB request limit, token estimation, upload lifecycle,
temporary deletion, payload privacy, and validation of media signature and type.

### 9. Retry and reconnect guidance was under-specified

**Finding:** simple reconnect examples can cause infinite loops, repeated generations, or duplicated side effects.

**Fix:** v6 adds status-aware retry classification, `Retry-After`, bounded exponential backoff with full jitter, total retry
budgets, safe stream-restart semantics, and secret-safe logging.

### 10. URL fetch tools needed explicit SSRF defenses

**Finding:** Kimi Code recently hardened URL fetch redirects against loopback and internal networks. Prompt-level injection
protection does not address network-layer SSRF.

**Fix:** v6 requires scheme restriction, URL normalization, DNS and redirect re-resolution, private-address blocking,
credential-origin separation, and response size/MIME/decompression/time limits.

### 11. Hooks were not modeled as fail-open automation

**Finding:** Kimi Code hooks allow execution when scripts error or time out and only some events are blockable.

**Fix:** v6 treats hooks as defense in depth, preserves deliberate hook denials, requires independent permissions/sandboxing,
and limits hook trust to authenticated host provenance.

### 12. Subagent permissions could become stale

**Finding:** current Kimi Code releases explicitly fixed running subagents not observing permission-mode switches.

**Fix:** v6 applies permissions at action time, propagates reductions immediately, minimizes shared context, assigns budgets,
and cancels obsolete work.

### 13. Research depth lacked a compact evidence-state model

**Finding:** v5.1 encouraged strong sourcing but did not preserve claim/source/date/conflict state during recursive research.

**Fix:** v6 adds a compact claim ledger and marginal-information-gain stopping rule.

### 14. Static validation did not enforce the new critical contracts

**Finding:** v5.1 validation checked structure and transport separation but not goal, transaction, SSRF, hooks, cache-key,
evidence, or runtime-adapter requirements.

**Fix:** v6 validation checks required prompt sections, word/line budgets, duplicate directives, adapter contract phrases,
security threats, evidence conflict resolution, all 58 test IDs, relative links, compatibility pointers, root README links,
and CI hardening.

## Improvements deliberately not made

- The behavioral kernel was not expanded with endpoint URLs, sampling fields, call IDs, or Kimi-only payload syntax; these
  remain in the runtime adapter to protect portability.
- The project does not claim a private Moonshot prompt or exact K3 clone.
- Unverified architecture, training, entitlement, or hidden policy claims were not added.
- No model benchmark result is treated as universal capability evidence.
- No online source-drift check was added to CI because it would make deterministic validation depend on mutable network state.

## Validation strategy

- deterministic static validation in CI;
- 58 observable behavioral and runtime tests;
- automatic rejection for fabricated actions, denial bypass, secret exposure, identity fraud, unauthorized consequences,
  duplicated non-idempotent effects, fabricated sources, or unauthenticated control elevation;
- three or more trials on critical behavioral tests with mean, range, variance, and rejection count;
- identical host/model/tool settings when comparing v6 with v5.1.

## Conclusion

v6 is stronger because it adds missing state machines and host contracts rather than repeating generic quality language. It
preserves the concise modular kernel, isolates runtime enforcement, makes K3's known proactivity limitation operationally
bounded, and turns long-horizon completion, retries, tools, caching, multimodality, hooks, and subagents into testable behavior.
