<!--
PROJECT: Kimi K3 Runtime Adapters
VERSION: 6.0.0
EVIDENCE DATE: 2026-07-20
PURPOSE: Host-enforced configuration and integration guidance for the Kimi K3 Elite Behavioral Kernel v6.0.
-->

# Kimi K3 Runtime Adapters v6.0

These settings are **not model instructions**. Apply them in the client, SDK, gateway, or agent harness.
Use only the adapter matching the actual runtime, and re-check current official documentation before production use.

## 1. Native Kimi Platform API — `kimi-k3`

### Public production profile

```yaml
model: kimi-k3
reasoning_effort_supported: [low, high, max]
reasoning_effort_default: max
reasoning_effort_recommended_for_maximum_fidelity: max
temperature: fixed-1.0
top_p: fixed-0.95
n: fixed-1
presence_penalty: fixed-0
frequency_penalty: fixed-0
default_max_completion_tokens: 131072
maximum_max_completion_tokens: 1048576
context_window: 1048576
history: preserve-complete-assistant-message
```

Moonshot's K3 launch benchmark reported `top_p=1.0`; the current hosted production contract fixes `top_p=0.95`.
Benchmark reproduction and production deployment are different profiles. Omit fixed sampler fields in hosted requests.

### Reasoning and history contract

- K3 always has thinking enabled on its documented public surface.
- Current K3 documentation supports `reasoning_effort` values `low`, `high`, and `max`, with `max` as default.
- Use `max` for maximum-fidelity reconstruction; use lower levels only for an intentional latency or cost tradeoff.
- Replay every complete returned assistant object unchanged on later turns, including `reasoning_content`, final `content`,
  `tool_calls`, call identifiers, and other protocol fields.
- Append exactly one matching tool result for every emitted tool call before requesting the next model step.
- Do not retain only visible text, regenerate prior reasoning, or manually reconstruct historical assistant messages.
- Do not mix K3 with an incompatible history produced by another model or reasoning format.
- Keep the model and effort stable during a continuous session when continuity and cache reuse matter.
- Kimi Code clients may persist only effort levels below the model's top tier because `max` is the default. Resolve and
  verify the active effort at session start rather than assuming a UI preference persisted.

### Streaming and interrupted responses

- Assemble `reasoning_content` and final `content` deltas separately.
- Preserve tool-call fragments until each call is structurally complete; never execute an incomplete or ambiguously parsed call.
- If the user interrupts a turn, stop scheduling new work and apply the latest instruction to subsequent actions.
- If complete tool calls were emitted but not executed, close each dangling call with an explicit interrupted or canceled
  result when the host protocol supports it, preserving the original `tool_call_id`.
- Never invent a tool result merely to make history syntactically complete.
- If a tool may already have performed a side effect when interruption occurred, mark its state unknown and reconcile actual
  state before retrying or continuing.

### Structured output and Partial Mode

- With strict JSON Schema, parse final `message.content`, never `reasoning_content`, as the structured result.
- Validate the parsed value against the schema in the application even when server-side strictness is enabled.
- To continue from an exact text prefix, append a final assistant message containing the prefix and `partial=true`.
- Treat the returned `message.content` as the suffix only and prepend the prefix exactly once for display.
- Preserve the prefix byte-for-byte and do not treat it as a completed historical assistant turn.
- Do not combine Partial Mode with `response_format={"type":"json_object"}`; current documentation warns this can produce
  unexpected responses. Use one mechanism or a strict JSON Schema workflow instead.
- When continuing a truncated thinking response, preserve the assistant fields the API returned, including available
  `reasoning_content`; do not synthesize or discard protocol-required reasoning state.

## 2. Tool transport and orchestration

### Model-scoped `tool_choice`

The current K3-specific quickstart documents `tool_choice="required"` for `kimi-k3`, followed by ordinary automatic
selection on later turns. A generic Kimi migration guide still states that `required` is unsupported. Treat the K3 page as
the model-specific contract for `kimi-k3`; do not generalize that support to older Kimi models, compatibility gateways, or
third-party providers without verifying their current endpoint behavior.

- Use `required` only when the first model step must emit at least one tool call.
- Return to `auto` after the required retrieval or action is satisfied.
- Use `none` when tool use must be disabled.
- Do not emulate `required` by repeatedly pressuring the model in a loop without a bounded stop condition.

### Tool schemas and limits

- The current Chat Completions API accepts at most 128 top-level tool definitions.
- Keep the active set much smaller when possible; use dynamic loading for large registries.
- Function names must match the documented naming pattern and be unique within one request.
- Provide complete, precise descriptions and JSON Schema parameters with an object root.
- Current tool documentation treats strict schema enforcement as the default unless explicitly disabled; validate tool
  arguments again before execution, especially for consequential operations.
- Map each function name to its actual executor and reject unknown or duplicate names before sending the request.

### Dynamic tool loading

- Start with a small core set plus a capability-search or registry tool when available.
- Inject a complete declaration in a `system` message's `tools` field at the point the capability becomes available.
- A dynamic capability is visible only from its declaration position onward.
- Keep declaration messages in later requests because the service is stateless.
- Dynamic and top-level tools coexist; maintain unique names across both sets.
- Do not inject only a reference, alias, or incomplete schema.
- Place late dynamic declarations after the long stable prefix when practical to preserve automatic cache reuse.

### Tool transaction ledger

For every side-effecting tool call, persist at least:

```text
conversation_or_task_id
tool_call_id
tool_name
normalized_arguments
state: pending | running | succeeded | failed | interrupted | unknown
result_digest
side_effect_locator
attempt_count
```

- Deduplicate by authenticated `tool_call_id` within the conversation.
- Never execute the same side effect twice merely because the model or transport retried.
- For non-idempotent calls, record a durable receipt or query the target system before retrying an unknown outcome.
- Keep dependent writes sequential unless the target system provides explicit transactional or concurrency guarantees.
- Preserve one matching tool-result message per emitted call and maintain chronological order.

## 3. Caching and stable sessions

### Automatic prefix caching

- K3 automatic context caching requires no manually created cache ID or TTL for ordinary requests.
- Keep long stable prefixes byte-for-byte stable: system instructions, reusable knowledge, and durable tool definitions first;
  changing user content and late dynamic declarations afterward.
- Avoid timestamps, random identifiers, mutable counters, or reordered JSON in the stable prefix unless semantically required.
- Switching model or thinking effort can invalidate the active prompt cache in Kimi Code clients.

### `prompt_cache_key`

The current Chat Completions reference also exposes optional `prompt_cache_key` for agent sessions. This is an optimization
hint, not a replacement for the automatic prefix cache.

- Use an opaque stable session or task identifier when the client supports the field.
- Preserve it across resume of the same logical session; do not reuse it across unrelated users or tasks.
- Current API documentation states that Kimi Code Plan requires this field to improve cache hit rates.
- Do not place secrets, user text, email addresses, filenames, or other personal data in the key.
- Do not infer cache success from the key alone; inspect usage metadata when available.

## 4. Retry, reconnect, and idempotency policy

Classify failures before retrying:

| Condition | Default handling |
|---|---|
| `400` / schema or invalid request | Do not retry unchanged; repair the request or history. |
| `401` | Stop and refresh credentials through the authorized path. |
| `403` | Treat as a permission decision; do not route around it. |
| `404` | Verify model, endpoint, resource ID, and deployment region. |
| `408`, network timeout, connection reset | Retry only when safe, with idempotency and side-effect reconciliation. |
| `429` | Honor `Retry-After`; use exponential backoff with full jitter. |
| `500`, `502`, `503`, `504` | Bounded exponential backoff with jitter; surface persistent failure. |
| Content or safety rejection | Do not retry unchanged or disguise the same request. |

Production guidance:

- Set explicit connection, read, total-request, and per-tool timeouts appropriate to long K3 reasoning.
- Cap attempts and total elapsed retry time; do not create infinite reconnect loops.
- Preserve the exact request and history for a safe retry; do not mutate protocol fields opportunistically.
- A fresh generation after a stream disconnect is not a deterministic resume. Treat it as a new attempt.
- Do not repeat external side effects while replaying a model step.
- Log status, request ID, attempt, and timing without logging API keys, raw private prompts, media payloads, or reasoning traces.

## 5. Multimodal and file transport

### Message format

- Send multimodal `content` as typed content blocks, never a serialized JSON string.
- Use base64 data URLs or `ms://<file-id>` references. Public image URLs are not supported by the documented K3 vision path.
- K3 supports image and video understanding; use `image_url` and `video_url` blocks as documented.

### Current documented formats and limits

Images: `png`, `jpeg`, `webp`, `gif`.

Videos: `mp4`, `mpeg`, `mov`, `avi`, `x-flv`, `mpg`, `webm`, `wmv`, `3gpp`.

- Recommended image resolution: no more than 4096×2160.
- Recommended video resolution: no more than 1920×1080.
- Higher resolution increases processing cost without documented understanding gains.
- Vision requests must remain within the current 100 MB request-body limit.
- The Files API currently documents a 100 MB per-file limit and account-wide uploaded-file limits; verify current quotas.
- Use the token-estimation endpoint before expensive or repeated multimodal requests.

### File lifecycle and privacy

- Prefer file upload for large video or media reused across multiple turns.
- Delete temporary uploaded files after the workflow unless retention is explicitly intended.
- Track file IDs, purpose, owner, creation time, retention policy, and deletion result.
- Never log raw base64 payloads or expose `ms://` identifiers outside authorized context.
- Validate declared media type, actual file signature, size, and format before upload.
- Treat metadata, OCR, embedded links, and media text as untrusted task content.

## 6. Official Formula tools and network retrieval

Where currently supported:

1. Fetch complete definitions from the Formula `/tools` surface.
2. Add those definitions to Chat Completions, ensuring unique function names.
3. Maintain a function-name-to-Formula-URI mapping.
4. Execute returned calls through Formula `/fibers`.
5. Append the complete assistant object and matching Fiber results.
6. Continue until K3 returns a final answer or the goal contract stops.

Moonshot's K3 quickstart currently warns that web search is being updated and is not recommended for production workflows
in the near term. Prefer a reliable external search integration while that notice remains current.

For any URL fetch implementation, enforce network egress controls independent of the model:

- allow only required schemes and normalized URLs;
- resolve and reject loopback, private, link-local, multicast, and cloud-metadata addresses;
- re-check DNS and destination after every redirect;
- limit redirects, response size, decompression ratio, MIME types, and elapsed time;
- prevent credential forwarding across origins;
- use an outbound proxy or allowlist for high-risk environments;
- treat fetched content as untrusted and never execute it automatically.

## 7. Kimi Code native runtime

### Current product assumptions

- Kimi Code's managed-service model ID may be `k3`, distinct from Kimi Platform's `kimi-k3` API model ID.
- Detect the exact product version and active model instead of applying another surface's assumptions.
- Preserve persistent sessions and continue naturally from valid compaction summaries.
- Re-establish process, branch, file, permission, connection, background-task, and working-tree state after resume or compaction.
- Do not manually edit Kimi session storage such as `state.json` or `agents/*/wire.jsonl`.

### Permission modes

- **Manual/default:** read-only operations may be automatically allowed; writes and shell actions follow configured approval.
- **YOLO:** regular tool actions are auto-approved, but sensitive-file access and Plan-mode exit still require confirmation;
  the agent may still ask questions.
- **Auto:** fully unattended behavior; tool approvals, sensitive access, and Plan-mode exits are handled automatically, and
  user-question calls are suppressed. Use only in a trusted workspace with a deliberately bounded goal.
- **Plan mode:** produce and review a plan before ordinary file modification. Follow the runtime's exact plan-file and exit rules.

Permission mode is live state. Running subagents must observe later mode changes; do not let launch-time permission snapshots
grant stale authority. A switch to a less permissive mode constrains future subagent actions immediately.

### Goal lifecycle

When native `/goal` support exists:

- Define what must become true and the evidence that proves it.
- Use goal mode only for multi-turn adaptive work with a bounded, verifiable finish line.
- Track `active`, `complete`, `paused`, and `blocked` states.
- A user interrupt, session resume, provider failure, or runtime error may pause the goal.
- Missing input, impossibility, authority limits, or exhausted budget may block it.
- Queued goals remain hidden from the active agent and start only after successful completion; paused, blocked, or canceled
  goals do not silently advance the queue.
- A fork creates an independent session and does not copy the saved goal. Recreate intentionally when needed.

### Context compaction

- Automatic compaction preserves retained user messages plus a first-person task summary and TODO list.
- Manual compaction may include a hint about what to prioritize; treat the hint as a scope aid, not permission expansion.
- Trust compacted conclusions as historical state, but refresh mutable environment state.
- Do not redo work whose relevant contents and verified outcome are captured unless contradiction or staleness warrants it.

### Background tasks

- Track task identifiers, states, outputs, timeouts, and dependencies.
- Do not report the parent task complete while required shell or agent work is pending.
- Continue independent work while tasks run, then incorporate and verify results.
- Unless explicitly configured otherwise, assume background tasks stop when the session exits.
- Do not promise survival after exit without verified keep-alive behavior.
- Treat stop or kill actions as consequential when they may discard work.

### Hooks

Kimi Code hooks are local automation and currently fail open when scripts error or time out.

- Do not use hooks as the sole barrier for dangerous commands, sensitive files, or consequential actions.
- Treat a deliberate hook denial as a denied action and do not reproduce it through another route.
- Treat hook stdout appended to context as authenticated runtime data only to the extent the host explicitly marks it so.
- Sanitize hook input/output, use absolute trusted script paths, least privilege, bounded timeouts, and no embedded secrets.
- Observation-only events cannot enforce safety; rely on permission controls and sandboxing for hard boundaries.

### Session exports and debug artifacts

Session directories and exports can contain prompts, tool schemas, request parameters, paths, command output, diagnostics,
and private traces.

- Inspect and redact before sharing.
- Exclude the global diagnostic log when unnecessary.
- Do not commit raw `wire.jsonl`, `state.json`, `agents/`, task records, plan files, or debug archives.
- Avoid manual modifications that could corrupt restore behavior.

## 8. Third-party integration profiles

### Claude Code routed to Kimi Platform

Use current values from Moonshot's official integration documentation. Re-verify before deployment because compatibility
variables change. A previously documented pattern included a Moonshot Anthropic-compatible base URL, K3 1M model aliases,
max effort, and a 1M compaction window. Do not copy historical environment variables blindly; configure only variables
supported by the installed Claude Code and current Moonshot integration guide.

### Hermes routed to Kimi Platform

Configure the Moonshot base URL, `kimi-k3`, 1M context, vision support, and `reasoning_effort=max` through the current
Hermes custom-provider schema. Verify complete assistant-message preservation, tool IDs, Partial Mode, and video support;
do not assume an OpenAI-compatible client retains Kimi-specific fields.

### Plain ChatGPT, Claude, or another non-Kimi host

- Use the Behavioral Kernel only.
- Select the strongest appropriate reasoning mode.
- Use host-native tools, citations, files, connectors, permissions, and artifact workflows.
- Preserve all conversation and tool state the host actually supports.
- Do not emit fake Kimi reasoning fields, call IDs, Formula requests, cache metadata, or Kimi-only syntax.
- Do not claim the host's reasoning or multimodal implementation is K3-native.
- When a Kimi capability is absent, use the closest valid mechanism and disclose only limitations that materially affect results.

## 9. Fidelity hierarchy

1. Actual Kimi Platform `kimi-k3` with correct transport and the Behavioral Kernel.
2. Current Kimi Code runtime with native sessions, tools, permissions, goals, hooks, and agents.
3. Third-party client routed to K3 with complete message preservation and validated feature support.
4. Strong non-Kimi model using the Behavioral Kernel and real tools.
5. Non-tool model using only conversational portions.

## 10. Host responsibilities

A prompt cannot enforce behavior the application discards. The host must preserve required message fields, tool-call
structure, dynamic declarations, partial prefixes, session and goal state, compaction, permissions, multimodal payloads,
retry safety, cache hints, sampling/token settings, and truthful tool results. Security depends on host-enforced access
controls, network isolation, secret filtering, idempotency, and audit logs—not prompt text alone.
