from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
import tempfile


class BanditError(Exception):
    """Raised when the Bandit scan fails in a non recoverable way."""


def run_bandit(
    path: str,
    severity_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the Bandit Python security analyzer on a file or directory.

    Parameters
    ----------
    path:
        Path to a single .py file or a directory containing Python code.
    severity_filter:
        Optional severity filter: 'LOW', 'MEDIUM', or 'HIGH'.
        If provided, only results with that issue_severity are returned.
        Summary counts are still computed for all severities.

    Returns
    -------
    dict
        A compact JSON-like structure with:
        - path: scanned path
        - summary: totals per SEVERITY level (from Bandit metrics)
        - results: list of findings with filename, line_number,
                   issue_severity, issue_text, and test_id
        - errors: list of Bandit errors, if any
        - generated_at: timestamp string from Bandit

    Notes
    -----
    This function does not execute the target code. Bandit performs static
    analysis on the source AST only.
    """

    target = Path(path)
    if not target.exists():
        raise BanditError(f"Target path does not exist: {path}")

    # Build the Bandit command.
    # For directories, we use recursive mode (-r).
    # For single files, we pass the file path directly.
    if target.is_dir():
        cmd = ["bandit", "-r", str(target), "-f", "json"]
    else:
        cmd = ["bandit", str(target), "-f", "json"]

    try:
        completed = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        # bandit CLI not installed or not on PATH
        raise BanditError(
            "Bandit executable not found. "
            "Make sure 'bandit' is installed in this virtual environment."
        ) from exc

    # Bandit exits with code 1 when issues are found, and 0 when none are found.
    # Codes > 1 indicate an error. 
    if completed.returncode not in (0, 1):
        raise BanditError(
            f"Bandit failed with exit code {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise BanditError("Failed to parse Bandit JSON output.") from exc

    # Example JSON shape from the official docs: metrics._totals and results[]. 
    metrics = data.get("metrics", {})
    totals = metrics.get("_totals", {})
    raw_results: List[Dict[str, Any]] = data.get("results", [])
    errors = data.get("errors", [])
    generated_at = data.get("generated_at")

    # Build severity summary from the totals keys like 'SEVERITY.HIGH'
    summary: Dict[str, int] = {}
    for key, value in totals.items():
        if key.startswith("SEVERITY."):
            # Keep the original key, eg 'SEVERITY.HIGH'
            try:
                summary[key] = int(value)
            except (TypeError, ValueError):
                # If Bandit returns something unexpected, skip this key.
                continue

    # Build compact result entries
    severity_filter_normalized: Optional[str] = (
        severity_filter.upper() if severity_filter else None
    )

    compact_results: List[Dict[str, Any]] = []
    for issue in raw_results:
        sev = issue.get("issue_severity")
        if severity_filter_normalized and sev != severity_filter_normalized:
            continue

        compact_results.append(
            {
                "filename": issue.get("filename"),
                "line_number": issue.get("line_number"),
                "issue_severity": sev,
                "issue_text": issue.get("issue_text"),
                "test_id": issue.get("test_id"),
            }
        )

    return {
        "path": str(target),
        "summary": summary,
        "results": compact_results,
        "errors": errors,
        "generated_at": generated_at,
    }

def evaluate_patch(
    file_path: str,
    patched_content: str,
    severity_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate a patch by comparing Bandit results before and after.

    Parameters
    ----------
    file_path:
        Path to the original Python file on disk.
    patched_content:
        Full text of the patched version of the file.
    severity_filter:
        Optional severity filter ('LOW', 'MEDIUM', 'HIGH') passed through to
        run_bandit for both before and after scans.

    Returns
    -------
    dict
        {
          "original_path": "<file_path>",
          "original_summary": {...},    # Bandit summary before
          "patched_summary": {...},     # Bandit summary after
          "delta": {                    # patched - original per severity key
             "SEVERITY.HIGH": -1,
             ...
          }
        }

    Notes
    -----
    This function does not execute the target program. It only runs Bandit on
    the original file path and on a temporary file containing the patched
    content.
    """

    # 1. Bandit on original file
    original = run_bandit(path=file_path, severity_filter=severity_filter)
    original_summary = original.get("summary", {})

    # 2. Write patched content to a temporary file and run Bandit again
    original_path = Path(file_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / original_path.name
        tmp_file.write_text(patched_content, encoding="utf-8")

        patched = run_bandit(path=str(tmp_file), severity_filter=severity_filter)
        patched_summary = patched.get("summary", {})

    # 3. Compute delta: patched - original per severity key
    all_keys = set(original_summary.keys()) | set(patched_summary.keys())
    delta: Dict[str, int] = {}
    for key in all_keys:
        before = int(original_summary.get(key, 0))
        after = int(patched_summary.get(key, 0))
        delta[key] = after - before

    return {
        "original_path": str(original_path),
        "original_summary": original_summary,
        "patched_summary": patched_summary,
        "delta": delta,
    }