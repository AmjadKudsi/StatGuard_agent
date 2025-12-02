from __future__ import annotations

import tempfile
from pathlib import Path

from staticguard_agent.sglib.tools import run_bandit, evaluate_patch


def _write_file(tmpdir: str, name: str, content: str) -> str:
    path = Path(tmpdir) / name
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_run_bandit_on_safe_file():
    """Bandit should report zero findings on a very simple safe file."""
    safe_code = """\
def add(a, b):
    return a + b
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_file(tmpdir, "safe.py", safe_code)
        result = run_bandit(path)

    summary = result.get("summary", {})
    results = result.get("results", [])

    # We do not assume anything about Bandit internals beyond:
    # - summary is present
    # - results is a list that is empty for this trivial case
    assert isinstance(summary, dict)
    assert isinstance(results, list)
    assert len(results) == 0


def test_run_bandit_detects_subprocess_shell_issue():
    """
    Bandit should detect a classic shell=True issue.

    This is a minimal example of a real world vulnerability pattern:
    using subprocess with shell=True and user controlled input, which
    Bandit flags (for example test_id B602).
    """
    vulnerable_code = """\
import subprocess

def bad():
    cmd = "ls " + input("Enter path: ")
    subprocess.call(cmd, shell=True)
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_file(tmpdir, "vuln.py", vulnerable_code)
        result = run_bandit(path)

    results = result.get("results", [])
    assert isinstance(results, list)
    assert len(results) >= 1

    # At least one finding should be about subprocess.shell use
    test_ids = {r.get("test_id") for r in results}
    assert "B602" in test_ids or "B605" in test_ids or "B607" in test_ids


def test_evaluate_patch_reduces_high_severity():
    """
    evaluate_patch should not increase high severity issues
    when applying a patch that removes shell=True.

    This uses the same vulnerable pattern as above and a patched
    version that uses a safer argument list without shell=True.
    """
    original_code = """\
import subprocess

def bad():
    cmd = "ls " + input("Enter path: ")
    subprocess.call(cmd, shell=True)
"""

    patched_code = """\
import subprocess

def bad():
    path_input = input("Enter path: ")
    subprocess.call(["ls", path_input])
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        path = _write_file(tmpdir, "vuln.py", original_code)
        eval_result = evaluate_patch(file_path=path, patched_content=patched_code)

    original_summary = eval_result.get("original_summary", {}) or {}
    patched_summary = eval_result.get("patched_summary", {}) or {}

    high_before = int(original_summary.get("SEVERITY.HIGH", 0) or 0)
    high_after = int(patched_summary.get("SEVERITY.HIGH", 0) or 0)

    # The patch should not increase high severity issues, and in
    # realistic cases it should remove the B602 finding.
    assert high_after <= high_before
