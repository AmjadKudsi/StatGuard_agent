from __future__ import annotations

from typing import Any, Dict, Optional

from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool

from .sglib.tools import run_bandit, evaluate_patch
from .sub_agents import scanner_agent, fixer_agent


def scan_repo(path: str, severity_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool: Run Bandit on a Python file or directory and return a compact JSON
    structure with summary metrics and findings.

    Parameters
    ----------
    path:
        Path to a Python file or directory.
    severity_filter:
        Optional severity filter: 'LOW', 'MEDIUM', or 'HIGH'.

    Returns
    -------
    dict
        See run_bandit for the exact structure.
    """
    return run_bandit(path=path, severity_filter=severity_filter)


def evaluate_patch_tool(
    file_path: str,
    patched_content: str,
    severity_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tool: Compare Bandit results before and after applying a patch to a file.

    The agent should pass the original file path and the FULL patched file
    content. The tool runs Bandit on the original file and on a temporary
    file containing the patched content, then returns summaries and deltas.
    """
    return evaluate_patch(
        file_path=file_path,
        patched_content=patched_content,
        severity_filter=severity_filter,
    )

# Wrapping subagents as tools for the coordinator (Agent-as-a-Tool pattern). 
scanner_tool = AgentTool(agent=scanner_agent, skip_summarization=False)
fixer_tool = AgentTool(agent=fixer_agent, skip_summarization=False)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="staticguard_root",
    description=(
        "StaticGuard: a non-executing static security assistant for Python code."
    ),
    instruction=(
        "You are StaticGuard, an assistant that uses Bandit (a static security "
        "analyzer for Python) to detect issues and evaluate patches.\n\n"
        "Tools available:\n"
        "1) scan_repo(path, severity_filter=None): run Bandit on a file or "
        "directory and return a JSON summary of findings.\n"
        "2) evaluate_patch_tool(file_path, patched_content, "
        "severity_filter=None): run Bandit on the original file and on a "
        "temporary file containing the patched content, then return severity "
        "summaries and their difference.\n\n"
        "When the user asks to improve or fix a specific Bandit finding in a "
        "file, follow this pattern:\n"
        "- First, call scan_repo to understand the current issues.\n"
        "- Propose a SMALL, LOCAL patch that only modifies the function or "
        "small region that contains the issue. Avoid refactoring unrelated "
        "code.\n"
        "- Produce both (a) the full patched file content and (b) a unified "
        "diff for the user to review.\n"
        "- Then call evaluate_patch_tool with the original file path and the "
        "FULL patched content to compute Bandit metrics before and after.\n"
        "- Finally, explain the metrics (original vs patched, including delta) "
        "and whether the patch seems to reduce or introduce issues.\n\n"
        "Never claim to have executed the code or tests. You only perform "
        "static analysis using Bandit."
    ),
    tools=[scan_repo, evaluate_patch_tool],
    )