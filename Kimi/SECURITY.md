# Security Model for the Kimi K3 Reconstruction v5.1

## Scope

This document covers the security properties of the portable behavioral kernel, runtime adapters, evaluation suite,
and contributor workflow in this directory. It does not audit Moonshot AI's private infrastructure or model internals.

## Protected assets

- user intent and approved scope;
- confidential data, credentials, private files, and connected-account information;
- system, developer, and authenticated runtime instructions;
- tool permissions and approval decisions;
- repository integrity and uncommitted work;
- correctness of tool results, citations, files, and completion claims;
- session records that may contain prompts, paths, command output, or sensitive traces.

## Trust boundaries

From highest to lowest:

1. host policies and authenticated system, developer, and runtime controls;
2. current tool schemas, permission controls, and environment constraints;
3. direct user instructions;
4. project guidance, skills, plugins, and accepted prior task context;
5. retrieved or user-supplied content.

Scope precedence such as `Project > User > Extra > Built-in` applies only among same-layer skills. It never elevates a
skill or project file above a direct user instruction.

## Threats and invariants

### Control-channel spoofing

Task content may imitate the host's control-message syntax.

**Invariant:** syntax alone never grants authority. Only provenance authenticated by the host can elevate control data.

### Malicious project guidance or capability metadata

A project file, skill, plugin, or connector description may attempt to expand scope, alter permissions, or redirect work.

**Invariant:** these sources stay below the user unless the authenticated host explicitly elevates a specific contract.
Same-name scope precedence resolves only conflicts among capabilities in the same layer.

### Permission-denial circumvention

A refused action may be attempted through shell, another connector, a subagent, or an indirect equivalent.

**Invariant:** denial is a policy decision. The agent must not reproduce the refused action through another mechanism.

### Consequential-action overreach

The agent may attempt destructive, external, costly, production, account, git, messaging, publication, or permission
changes without sufficiently scoped authorization.

**Invariant:** approval is action- and context-specific unless a durable higher-priority rule clearly authorizes a class.

### Private-context propagation

Subagent prompts, logs, session files, task records, or debug bundles may contain private context.

**Invariant:** pass only minimum necessary context. Inspect and redact before publishing. Do not commit raw `wire.jsonl`,
`state.json`, `agents/`, `tasks/`, plan files, or debug bundles.

### False tool or completion claims

The model may infer success from a missing error or report completion while checks or background work remain unfinished.

**Invariant:** inspect material results, wait for required background work, verify the deliverable, and label untested work.

### Transport confusion

A portable host may be instructed to emit Kimi-only fields, or a Kimi client may discard required history, identifiers,
dynamic declarations, partial prefixes, or reasoning fields.

**Invariant:** behavioral instructions live in the kernel; transport rules live in the matching runtime adapter and must be
enforced by the host.

## Secure deployment checklist

- Use only the system-prompt boundary from the behavioral kernel.
- Apply exactly one matching runtime adapter.
- Verify actual model and provider identity.
- Preserve the selected API's required message and tool structure.
- Verify permission-mode behavior for the exact product and version.
- Constrain high-impact capabilities not needed for the task.
- Use least-privilege connectors and workspace scope.
- Do not expose raw session or debug artifacts.
- Run `python Kimi/validate.py` after changes.
- Run critical evaluation tests at least three times and review variance.

## Residual limitations

A prompt cannot guarantee security against a malicious or defective host, connector, tool implementation, base model, or
runtime that mislabels untrusted content as privileged. Host-enforced sandboxing, permission controls, privacy filtering,
logging hygiene, and independent evaluation remain necessary.
