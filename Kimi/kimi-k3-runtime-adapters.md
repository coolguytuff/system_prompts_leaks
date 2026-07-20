<!--
PROJECT: Kimi K3 Runtime Adapters
VERSION: 5.0.0
EVIDENCE DATE: 2026-07-20
PURPOSE: Host-enforced configuration and integration guidance for the Kimi K3 Elite Behavioral Kernel v5.0.
-->

# Kimi K3 Runtime Adapters v5.0

These settings are **not model instructions**. Apply them in the client, SDK, gateway, or agent harness.
Use only the adapter matching the actual runtime.

## 1. Kimi Platform API — native `kimi-k3`

### Public production profile

```yaml
model: kimi-k3
reasoning_effort: max
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

Moonshot's launch benchmark reported `top_p=1.0`. That is an evaluation configuration, not the documented hosted
production value. Omit sampler overrides in hosted production requests.

### Reasoning and history contract

- K3 always reasons on the public Kimi Platform surface.
- Use top-level `reasoning_effort="max"` unless official documentation changes.
- Replay each complete returned assistant message unchanged on later turns, including `reasoning_content`, final
  `content`, `tool_calls`, and any other protocol fields.
- Append exactly one matching tool result for each emitted tool call.
- Do not keep only visible text or manually reconstruct historical assistant messages.
- Do not switch K3 into an incompatible history produced by another model or reasoning format.
- Keep model and effort stable through a continuous session.
- In streaming, assemble reasoning and final-content deltas separately.
- With strict JSON Schema, parse the final `message.content`, never `reasoning_content`, as the structured result.

### Tools and caching

- `tool_choice` supports `auto`, `none`, and `required` on the documented K3 surface.
- Use `required` only when an initial retrieval/action is necessary; normally return to `auto` afterward.
- For dynamic tool loading, inject complete schemas at the documented point in history and preserve declarations in
  later requests because the service is stateless.
- Preserve tool-call identifiers and append all matching results before requesting the next model step.
- Prefix caching is automatic. Keep long stable prefixes byte-for-byte stable where practical.
- Place stable system instructions, knowledge, and reusable tool declarations before changing user content.
- Do not invent cache IDs or TTLs.

### Multimodal transport

- Send multimodal message `content` as typed content blocks, not serialized pseudo-JSON.
- Use base64 data URLs or `ms://<file-id>` references where documented.
- Do not assume public image URLs are accepted by the Kimi Platform vision path.
- Use the Files API and preserved file references for native video where the endpoint requires it.

### Official Formula tools

Where currently supported and recommended:
1. Retrieve complete tool definitions from the Formula `/tools` surface.
2. Expose those definitions in the chat-completions `tools` field.
3. Execute returned tool calls through Formula `/fibers`.
4. Append the complete assistant message and matching tool results.
5. Continue until the model returns a final answer.

Moonshot's public documentation has warned that its built-in web-search path is being updated and may not be
recommended for near-term production. Prefer a reliable external search integration while that notice remains current.

## 2. Kimi Code — native runtime or managed service

### Behavioral/runtime assumptions

- Kimi Code's managed-service model ID is `k3`, distinct from Kimi Platform's `kimi-k3` ID.
- Use the effort levels documented for the specific Kimi Code product surface.
- Avoid switching model or effort mid-session when doing so invalidates prompt cache or continuity.
- Preserve persistent sessions and continue naturally from compaction summaries.
- Re-establish transient state after compaction; do not blindly trust process, branch, file, permission, or background-task state.
- Treat inherited “done” claims as unverified until final checks succeed.

### Tool and permission behavior

- Prefer dedicated read, glob, grep, edit, and write tools over raw shell when they fit.
- Run independent read-only investigation in parallel where supported.
- Keep dependent operations and writes sequential.
- Respect active manual, auto, YOLO, or plan-mode policy.
- Never circumvent a rejected call.
- Treat leaving plan mode as a distinct approval boundary where the runtime does.
- Do not perform git mutations or outward-facing actions without the authorization required by active policy.
- Treat the working directory as project root unless scope is explicitly expanded.
- Inspect applicable `AGENTS.md` and `README` guidance, while keeping system, tool, permission, and direct user
  instructions higher in priority.
- Never use shell to bypass secret or path guards.

### Built-in agent roles

When available:
- `explore` — read-only reconnaissance and repository/source mapping.
- `plan` — architecture, decomposition, implementation planning, and critique.
- `coder` — implementation, edits, tests, debugging, and verification.

Use nested agents or AgentSwarm only when supported and materially beneficial. Keep task descriptions focused,
contexts isolated, and returned results concise and decision-useful.

## 3. Claude Code routed to Kimi Platform

Use the exact current values from Moonshot's official integration documentation. The deep-research snapshot found this
configuration pattern:

```bash
export ANTHROPIC_BASE_URL="https://api.moonshot.ai/anthropic"
export ANTHROPIC_AUTH_TOKEN="${YOUR_MOONSHOT_API_KEY}"
export ANTHROPIC_MODEL="kimi-k3[1m]"
export ANTHROPIC_DEFAULT_OPUS_MODEL="kimi-k3[1m]"
export ANTHROPIC_DEFAULT_SONNET_MODEL="kimi-k3[1m]"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="kimi-k3[1m]"
export ANTHROPIC_DEFAULT_FABLE_MODEL="kimi-k3[1m]"
export CLAUDE_CODE_SUBAGENT_MODEL="kimi-k3[1m]"
export ENABLE_TOOL_SEARCH="false"
export CLAUDE_CODE_AUTO_COMPACT_WINDOW="1048576"
export CLAUDE_CODE_EFFORT_LEVEL="max"
```

Re-verify the official integration page before production deployment because client environment variables and
compatibility behavior can change.

## 4. Hermes routed to Kimi Platform

The deep-research snapshot found this documented pattern:

```yaml
custom_providers:
  - name: kimi-k3-global
    base_url: https://api.moonshot.ai/v1
    key_env: KIMI_API_KEY
    api_mode: chat_completions
    model: kimi-k3
    extra_body:
      reasoning_effort: max
    models:
      kimi-k3:
        context_length: 1048576
        supports_vision: true

model:
  provider: custom:kimi-k3-global
  default: kimi-k3
  context_length: 1048576
  supports_vision: true

agent:
  reasoning_effort: max
```

Re-verify current Hermes and Moonshot documentation before deployment, especially for video payload support and
message-field preservation.

## 5. Plain ChatGPT, Claude, or another non-Kimi host

- Use the Behavioral Kernel only.
- Select the strongest available reasoning mode appropriate to the task.
- Use host-native tools, citations, files, connectors, widgets, permissions, and artifact workflows.
- Preserve all conversation and tool state the host actually supports.
- Do not output fake `reasoning_content`, Kimi call IDs, Formula requests, cache metadata, or Kimi-only renderer syntax.
- Do not claim the host's reasoning or multimodal implementation is K3-native.
- When a Kimi capability is absent, use the closest valid host mechanism and disclose only limitations that materially
  affect the result.

## Fidelity hierarchy

1. Actual Kimi Platform `kimi-k3` with correct transport and behavioral kernel.
2. Kimi Code managed service or runtime with native sessions, tools, approvals, and agents.
3. Third-party client routed to Kimi with correct message preservation and configuration.
4. Strong non-Kimi model using the behavioral kernel and real tools.
5. Non-tool model using only the conversational portions.

## Host responsibilities

A model cannot enforce behavior the application discards. The host must preserve required message fields, tool-call
structure, dynamic declarations, session state, compaction, permissions, multimodal payloads, sampling/token settings,
and truthful tool results.
