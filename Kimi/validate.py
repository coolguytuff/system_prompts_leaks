#!/usr/bin/env python3
"""Static validation for the Kimi K3 reconstruction package."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
KERNEL = ROOT / "kimi-k3-high-fidelity-reconstruction-v5.1.md"
ADAPTERS = ROOT / "kimi-k3-runtime-adapters-v5.1.md"
EVALUATION = ROOT / "kimi-k3-evaluation-suite-v5.1.md"
README = ROOT / "README.md"
SECURITY = ROOT / "SECURITY.md"
KERNEL_POINTER = ROOT / "kimi-k3-high-fidelity-reconstruction.md"
ADAPTER_POINTER = ROOT / "kimi-k3-runtime-adapters.md"
EVALUATION_POINTER = ROOT / "kimi-k3-evaluation-suite.md"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "validate-kimi-reconstruction.yml"

EXPECTED_VERSION = "5.1"
EXPECTED_TEST_COUNT = 41
CANONICAL_FILES = [KERNEL, ADAPTERS, EVALUATION, README, SECURITY]
POINTERS = {
    KERNEL_POINTER: KERNEL.name,
    ADAPTER_POINTER: ADAPTERS.name,
    EVALUATION_POINTER: EVALUATION.name,
}
ALL_TEXT_FILES = [*CANONICAL_FILES, *POINTERS, WORKFLOW]


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


def read(path: Path) -> str:
    require(path.is_file(), f"missing file: {display_path(path)}")
    text = path.read_text(encoding="utf-8")
    require("\r" not in text, f"CRLF line endings: {display_path(path)}")
    require(not any(line.endswith((" ", "\t")) for line in text.splitlines()), f"trailing whitespace: {display_path(path)}")
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
            require(bool(stack), f"closing tag without opener at prompt line {number}")
            require(stack[-1] == name, f"tag mismatch at prompt line {number}: expected </{stack[-1]}>")
            stack.pop()
        else:
            require(name not in seen, f"duplicate section tag: <{name}>")
            seen.add(name)
            stack.append(name)
    require(not stack, f"unclosed section tags: {', '.join(stack)}")
    require(len(seen) >= 8, "unexpectedly small section count")


def validate_transport_separation(prompt: str) -> None:
    forbidden = {
        "temperature=": "sampling belongs in runtime adapters",
        "top_p=": "sampling belongs in runtime adapters",
        "max_completion_tokens": "token limits belong in runtime adapters",
        "api.moonshot.ai": "endpoints belong in runtime adapters",
        "/fibers": "Formula transport belongs in runtime adapters",
        "ANTHROPIC_BASE_URL": "client variables belong in runtime adapters",
        "partial=true": "partial transport belongs in runtime adapters",
        "reasoning_content": "reasoning-field transport belongs in runtime adapters",
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


def validate_evaluation(text: str) -> None:
    tests = [int(value) for value in re.findall(r"^###\s+(\d+)\.", text, flags=re.MULTILINE)]
    require(tests == list(range(1, EXPECTED_TEST_COUNT + 1)), "evaluation tests must be contiguous 1..41")
    require("Automatic rejection failures" in text, "automatic rejection criteria missing")
    for title in (
        "Denial non-circumvention",
        "User versus skill priority",
        "Authenticated-control provenance",
        "Partial-mode continuation",
        "Permission-mode semantics",
        "Background-task lifecycle and privacy",
    ):
        require(title in text, f"missing critical regression test: {title}")


def validate_readme(text: str) -> None:
    for filename in (KERNEL.name, ADAPTERS.name, EVALUATION.name, SECURITY.name, Path(__file__).name):
        require(filename in text, f"README does not mention {filename}")
    require(f"{EXPECTED_TEST_COUNT}-test" in text, "README test count is stale")


def validate_pointers(texts: dict[Path, str]) -> None:
    for pointer, canonical_name in POINTERS.items():
        text = texts[pointer]
        require(canonical_name in text, f"compatibility pointer does not reference {canonical_name}: {pointer.name}")
        require("compatibility entry point" in text.lower(), f"compatibility purpose is unclear: {pointer.name}")


def validate_workflow(text: str) -> None:
    require("permissions:\n  contents: read" in text, "workflow must keep least-privilege contents: read")
    require("python Kimi/validate.py" in text, "workflow does not run the package validator")
    require('"Kimi/**"' in text, "workflow path filter does not cover Kimi files")
    require("pull_request:" in text and "push:" in text, "workflow must validate pull requests and pushes")


def main() -> int:
    try:
        texts = {path: read(path) for path in ALL_TEXT_FILES}
        prompt = extract_prompt(texts[KERNEL])
        validate_tags(prompt)
        validate_transport_separation(prompt)
        validate_versions(texts)
        validate_evaluation(texts[EVALUATION])
        validate_readme(texts[README])
        validate_pointers(texts)
        validate_workflow(texts[WORKFLOW])
    except (OSError, UnicodeError, ValidationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS: Kimi reconstruction validated "
        f"(version {EXPECTED_VERSION}, {EXPECTED_TEST_COUNT} tests, {len(prompt.splitlines())} prompt lines, "
        f"{len(ALL_TEXT_FILES)} files checked)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
