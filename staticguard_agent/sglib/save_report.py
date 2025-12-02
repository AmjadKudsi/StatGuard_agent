from __future__ import annotations

from pathlib import Path


def save_report(path: str, report: str) -> str:
    """
    Save the report string to a text file.

    Parameters
    ----------
    path: str
        Full path to the output file, for example:
        /tmp/staticguard_report.txt
    report: str
        The markdown report string.

    Returns
    -------
    str
        A short status message with the path.
    """
    p = Path(path)
    p.write_text(report, encoding="utf-8")
    return f"Report saved to {p}"