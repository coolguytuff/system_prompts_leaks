#!/usr/bin/env python3
"""Deterministic static validation for the Kimi K3 reconstruction package."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent

KERNEL = ROOT / "kimi-k3-high-fidelity-reconstruction-v6.0.md"
ADAPTERS = ROOT / "kimi-k3-runtime-adapters-v6.0.md"
EVALUATION = ROOT / "kimi-k3-evaluation-suite-v6.0.md"
EVIDENCE = ROOT / "kimi-k3-evidence-v6.0.md"
AUDIT = ROOT / "kimi-k3-v6.0-audit.md"
README = ROOT / "README.md"
SECURITY = ROOT / "SECURITY.md"

KERNEL_POINTER = ROOT / "kimi-k3-high-fidelity-reconstruction.md"
ADAPTER_POINTER = ROOT / "kimi-k3-runtime-adapters.md"
EVALUATION_POINTER = ROOT / "kimi-k3-evaluation-suite.md"
ROOT_README = REPO_ROOT / "README.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate-kimi-reconstruction.yml"

EXPECTED_VERSION = "6.0"
EXPECTED_TEST_COUNT = 58
MIN_PROMPT_LINES = 250
MAX_PROMPT_LINES = 500
MAX_PROMPT_WORDS = 5200

CANONICAL_FILES = [KERNEL, ADAPTERS, EVALUATION, EVIDENCE, AUDIT, README, SECURITY]
POINTERS = {
    KERNEL_POINTER: KERNEL.name,
    ADAPTER_POINTER: ADAPTERS.name,
    EVALUATION_POINTER: EVALUATION.name,
}
ALL_TEXT_FILES = [*CANONICAL_FILES, *POINTERS, ROOT_README, WORKFLOW]

REQUIRED_TAGS = {
    "priority_and_provenance",
    "operating_posture",
    "task_router",
    "scope_control",
    "communication",
    "reasoning_and_evidence",
    "execution_loop",
    "goal_contract",
    "tools_and_permissions",
    "state_and_compaction",
    "task_modules",
    "integrity",
    "completion_gate",
}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def read(path: Path, *, enforce_final_newline: bool = True) -> str:
    require(path.is_file(), f"missing file: {display_path(path)}")
    text = path.read_text(encoding="utf-8")
    require("\r" not in text, f"CRLF line endings: {display_path(path)}")
    require(not any(line.endswith((" ", "\t")) for line in text.splitlines()), f"trailing whitespace: {display_path(path)}")
    if enforce_final_newline:
        require(text.endswith("\n"), f"missing final newline: {display_path(path)}")
    return text


def extract_prompt(text: str) -> str:
    begin = "## BEGIN SYSTEM PROMPT"
    end = "## END SYSTEM PROMPT"
    require(text.count(begin) == 1, "kernel must contain exactly one BEGIN marker")
    require(text.count(end) == 1, "kernel must contain exactly one END marker")
    start = text.index(begin) + len(begin)
    stop = text.index(end)
    require(start < stop, "system-prompt markers are reversed")
    prompt = text[start:stop].strip()
    require(prompt, "system-prompt boundary is empty")
    return prompt


def validate_tags(prompt: str) -> None:
    token = re.compile(r"^</?([a-z][a-z0-9_]*)>$")
    stack: list[str] = []
    seen: set[str] = set()
    for number, line in enumerate(prompt.splitlines(), start=1):
        stripped = line.strip()
        match = token.fullmatch(stripped)
        if not match:
            continue
        name = match.group(1)
        if stripped.startswith("</"):
            require(stack, f"closing tag without opener at prompt line {number}")
            require(stack[-1] == name, f"tag mismatch at prompt line {number}: expected </{stack[-1]}>")
            stack.pop()
        else:
            require(name not in seen, f"duplicate section tag: <{name}>")
            seen.add(name)
            stack.append(name)
    require(not stack, f"unclosed section tags: {', '.join(stack)}")
    missing = REQUIRED_TAGS - seen
    require(not missing, f"missing required section tags: {', '.join(sorted(missing))}")
    require(seen == REQUIRED_TAGS, f"unexpected section tag set: {', '.join(sorted(seen - REQUIRED_TAGS))}")


def validate_prompt_budget(prompt: str) -> None:
    lines = len(prompt.splitlines())
    words = len(re.findall(r"\S+", prompt))
    require(MIN_PROMPT_LINES <= lines <= MAX_PROMPT_LINES, f"prompt line count {lines} outside {MIN_PROMPT_LINES}..{MAX_PROMPT_LINES}")
    require(words <= MAX_PROMPT_WORDS, f"prompt word count {words} exceeds {MAX_PROMPT_WORDS}")

    normalized: list[str] = []
    in_fence = False
    for line in prompt.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or len(stripped) < 70 or stripped.startswith(("#", "<", "- **")):
            continue
        value = re.sub(r"\s+", " ", stripped).lower()
        normalized.append(value)
    duplicates = [line for line, count in Counter(normalized).items() if count > 1]
    require(not duplicates, f"duplicated long directives dilute priority: {duplicates[:3]}")


def validate_transport_separation(prompt: str) -> None:
    forbidden = {
        "temperature=": "sampling belongs in runtime adapters",
        "top_p=": "sampling belongs in runtime adapters",
        "max_completion_tokens": "token limits belong in runtime adapters",
        "api.moonshot.ai": "endpoints belong in runtime adapters",
        "/fibers": "Formula transport belongs in runtime adapters",
        "ANTHROPIC_BASE_URL": "client variables belong in runtime adapters",
        "partial=true": "Partial transport belongs in runtime adapters",
        "reasoning_content": "reasoning-field transport belongs in runtime adapters",
        "prompt_cache_key": "cache fields belong in runtime adapters",
    }
    lowered = prompt.lower()
    for needle, reason in forbidden.items():
        require(needle.lower() not in lowered, f"transport leakage: {needle!r} ({reason})")


def validate_versions(texts: dict[Path, str]) -> None:
    for path in CANONICAL_FILES:
        text = texts[path]
        require(
            f"v{EXPECTED_VERSION}" in text or f"VERSION: {EXPECTED_VERSION}.0" in text,
            f"version {EXPECTED_VERSION} missing from {display_path(path)}",
        )


def validate_runtime_adapter(text: str) -> None:
    required = {
        'tool_choice="required"': "K3-specific Tool Choice resolution",
        "prompt_cache_key": "agent cache-key guidance",
        "partial=true": "Partial Mode transport",
        "json_object": "Partial/JSON incompatibility",
        "128": "tool-array limit",
        "Retry-After": "rate-limit handling",
        "full jitter": "bounded retry strategy",
        "tool_call_id": "tool transaction identity",
        "interrupted": "interrupted-call closure",
        "loopback": "SSRF defense",
        "cloud-metadata": "metadata endpoint defense",
        "4096×2160": "image resolution guidance",
        "1920×1080": "video resolution guidance",
        "100 MB": "media/request limit",
        "fail open": "hook semantics",
        "Queued goals": "goal queue isolation",
        "permission mode is live state": "subagent permission propagation",
    }
    lowered = text.lower()
    for needle, reason in required.items():
        require(needle.lower() in lowered, f"runtime adapter missing {reason}: {needle}")


def validate_evaluation(text: str) -> None:
    tests = [int(value) for value in re.findall(r"^###\s+(\d+)\.", text, flags=re.MULTILINE)]
    require(tests == list(range(1, EXPECTED_TEST_COUNT + 1)), f"evaluation tests must be contiguous 1..{EXPECTED_TEST_COUNT}")
    require("Automatic rejection failures" in text, "automatic rejection criteria missing")
    for title in (
        "Scope-creep resistance",
        "Unknown side-effect reconciliation",
        "Goal proof conditions",
        "Queued-goal isolation",
        "Partial Mode versus JSON Mode",
        "Live permission-mode propagation",
        "Hook fail-open boundary",
        "Model-specific `tool_choice`",
        "Automatic cache versus `prompt_cache_key`",
        "SSRF and redirect defense",
        "Background-task lifecycle and session privacy",
    ):
        require(title in text, f"missing critical regression test: {title}")


def validate_evidence(text: str) -> None:
    for term in (
        "Kimi K3 API quickstart",
        "Kimi Code goals guide",
        "Kimi Code hooks guide",
        "tool_choice=\"required\"",
        "prompt_cache_key",
        "Conflict-resolution policy",
        "RECONSTRUCTED",
        "UNREPRODUCIBLE",
    ):
        require(term in text, f"evidence matrix missing: {term}")
    require("model-specific docs win for k3" in text.lower(), "evidence matrix does not resolve Tool Choice conflict")


def validate_security(text: str) -> None:
    for heading in (
        "Control-channel spoofing",
        "Excessive proactivity and scope drift",
        "Ambiguous or duplicated side effects",
        "Hook fail-open behavior",
        "SSRF and unsafe URL retrieval",
        "Cache-key correlation and data leakage",
        "Goal runaway and budget exhaustion",
        "Subagent permission drift",
        "Supply-chain and CI drift",
    ):
        require(heading in text, f"security model missing threat: {heading}")


def validate_readme(text: str) -> None:
    for filename in (KERNEL.name, ADAPTERS.name, EVALUATION.name, EVIDENCE.name, AUDIT.name, SECURITY.name, Path(__file__).name):
        require(filename in text, f"README does not mention {filename}")
    require(f"{EXPECTED_TEST_COUNT}-test" in text, "README test count is stale")


def validate_pointers(texts: dict[Path, str]) -> None:
    for pointer, canonical_name in POINTERS.items():
        text = texts[pointer]
        require(canonical_name in text, f"compatibility pointer does not reference {canonical_name}: {pointer.name}")
        require("compatibility entry point" in text.lower(), f"compatibility purpose is unclear: {pointer.name}")


def validate_relative_links(texts: dict[Path, str]) -> None:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in [*CANONICAL_FILES, *POINTERS]:
        for target in pattern.findall(texts[path]):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            require(resolved.is_file(), f"broken relative link in {path.name}: {target}")


def validate_root_readme(text: str) -> None:
    for target in POINTERS:
        require(f"Kimi/{target.name}" in text, f"root README missing Kimi entry: {target.name}")


def validate_workflow(text: str) -> None:
    require("permissions:\n  contents: read" in text, "workflow must keep least-privilege contents: read")
    require("python -m py_compile Kimi/validate.py" in text, "workflow does not compile validator")
    require("python Kimi/validate.py" in text, "workflow does not run validator")
    require('"Kimi/**"' in text and '"README.md"' in text, "workflow path filters are incomplete")
    require("pull_request:" in text and "push:" in text, "workflow must validate pull requests and pushes")
    require("persist-credentials: false" in text, "checkout credentials must not persist")
    require("timeout-minutes:" in text, "workflow job must have a timeout")

    action_refs = dict(re.findall(r"^\s*uses:\s+([^@\s]+)@([0-9a-f]{40})(?:\s+#.*)?$", text, flags=re.MULTILINE))
    for action in ("actions/checkout", "actions/setup-python"):
        require(action in action_refs, f"workflow action is not pinned to an immutable SHA: {action}")


def main() -> int:
    try:
        texts = {path: read(path, enforce_final_newline=path != ROOT_README) for path in ALL_TEXT_FILES}
        prompt = extract_prompt(texts[KERNEL])
        validate_tags(prompt)
        validate_prompt_budget(prompt)
        validate_transport_separation(prompt)
        validate_versions(texts)
        validate_runtime_adapter(texts[ADAPTERS])
        validate_evaluation(texts[EVALUATION])
        validate_evidence(texts[EVIDENCE])
        validate_security(texts[SECURITY])
        validate_readme(texts[README])
        validate_pointers(texts)
        validate_relative_links(texts)
        validate_root_readme(texts[ROOT_README])
        validate_workflow(texts[WORKFLOW])
    except (OSError, UnicodeError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    prompt_lines = len(prompt.splitlines())
    prompt_words = len(re.findall(r"\S+", prompt))
    print(
        "PASS: Kimi reconstruction validated "
        f"(version {EXPECTED_VERSION}, {EXPECTED_TEST_COUNT} tests, {prompt_lines} prompt lines, "
        f"{prompt_words} prompt words, {len(ALL_TEXT_FILES)} files checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
