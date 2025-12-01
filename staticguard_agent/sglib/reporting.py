from typing import Dict, Any


def build_basic_report(bandit_result: Dict[str, Any]) -> str:
    """
    Very simple markdown report builder for Step 0.

    Later we will include before/after metrics and diffs.
    """
    summary = bandit_result.get("summary", {})
    repo_path = bandit_result.get("repo_path", "<unknown>")

    high = summary.get("HIGH", 0)
    medium = summary.get("MEDIUM", 0)
    low = summary.get("LOW", 0)

    lines = [
        f"# StaticGuard report for `{repo_path}`",
        "",
        "## Bandit summary (stub)",
        "",
        f"- High: **{high}**",
        f"- Medium: **{medium}**",
        f"- Low: **{low}**",
    ]
    return "\n".join(lines)
