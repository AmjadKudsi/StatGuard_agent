from __future__ import annotations

from typing import Any, Dict, Tuple


def _extract_counts(summary: Dict[str, Any]) -> Tuple[int, int, int, int]:
    """
    Given a Bandit summary dict, return (total, high, medium, low).

    Summary is expected to contain keys like:
      "SEVERITY.HIGH", "SEVERITY.MEDIUM", "SEVERITY.LOW".
    Missing keys are treated as zero.
    """
    high = int(summary.get("SEVERITY.HIGH", 0) or 0)
    medium = int(summary.get("SEVERITY.MEDIUM", 0) or 0)
    low = int(summary.get("SEVERITY.LOW", 0) or 0)
    total = high + medium + low
    return total, high, medium, low


def build_markdown_report(
    path: str,
    eval_result: Dict[str, Any],
    diff: str,
    conclusion: str,
) -> str:
    """
    Build a compact markdown report for a single scan-and-fix attempt.

    Parameters
    ----------
    path:
        Original file path.
    eval_result:
        Result dict from evaluate_patch(), expected keys:
          - "original_summary"
          - "patched_summary"
          - "delta"
    diff:
        Unified diff as a string.
    conclusion:
        Short natural language conclusion from the LLM describing whether the
        patch improved, worsened, or did not change the situation.

    Returns
    -------
    str
        Markdown report string.
    """

    error = eval_result.get("error")
    if error:
        return (
            f"# StaticGuard evaluation for `{path}`\n\n"
            f"- Status: :x: Evaluation failed\n"
            f"- Reason: `{error}`\n"
        )

    original_summary = eval_result.get("original_summary") or {}
    patched_summary = eval_result.get("patched_summary") or {}
    delta = eval_result.get("delta") or {}

    # Extract severity counts
    total_before, high_before, med_before, low_before = _extract_counts(
        original_summary
    )
    total_after, high_after, med_after, low_after = _extract_counts(
        patched_summary
    )

    # Delta per severity and total
    d_high = int(delta.get("SEVERITY.HIGH", high_after - high_before) or 0)
    d_med = int(delta.get("SEVERITY.MEDIUM", med_after - med_before) or 0)
    d_low = int(delta.get("SEVERITY.LOW", low_after - low_before) or 0)
    d_total = total_after - total_before

    lines = []

    lines.append(f"# StaticGuard evaluation for `{path}`\n")
    lines.append("## Summary\n")
    lines.append(
        f"- Bandit findings before: **{total_before}** "
        f"(High: {high_before}, Medium: {med_before}, Low: {low_before})"
    )
    lines.append(
        f"- After patch: **{total_after}** "
        f"(High: {high_after}, Medium: {med_after}, Low: {low_after})"
    )
    lines.append(
        "- Delta (after - before): "
        f"(High: {d_high}, Medium: {d_med}, Low: {d_low}, Total: {d_total})"
    )

    lines.append("\n## Conclusion\n")
    if conclusion.strip():
        lines.append(conclusion.strip())
    else:
        lines.append(
            "No clear conclusion provided. Review the metrics above and the "
            "diff below to decide whether to accept this patch."
        )

    if diff.strip():
        lines.append("\n## Patch diff\n")
        lines.append("```diff")
        lines.append(diff.rstrip())
        lines.append("```")
    else:
        lines.append(
            "\n_No diff was provided for this patch attempt. No code changes "
            "are suggested._"
        )

    return "\n".join(lines) + "\n"
