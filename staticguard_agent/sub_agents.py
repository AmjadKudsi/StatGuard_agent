from __future__ import annotations

from typing import Any, Dict, Optional

from google.adk.agents.llm_agent import Agent

from .sglib.tools import run_bandit, evaluate_patch, load_file


def scan_repo(path: str, severity_filter: Optional[str] = None) -> Dict[str, Any]:
    """
    Shared tool wrapper for Bandit scans, for use by the scanner agent.
    """
    return run_bandit(path=path, severity_filter=severity_filter)


def evaluate_patch_tool(
    file_path: str,
    patched_content: str,
    severity_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Shared tool wrapper for patch evaluation, for use by the fixer agent.
    """
    return evaluate_patch(
        file_path=file_path,
        patched_content=patched_content,
        severity_filter=severity_filter,
    )


def load_file_tool(path: str) -> str:
    """
    Wrapper around load_file for use as an ADK tool.
    """
    return load_file(path)


scanner_agent = Agent(
    model="gemini-2.5-flash",
    name="scanner_agent",
    description="StaticGuard scanner that triages Bandit findings.",
    instruction=(
        "You are a static analysis triage assistant.\n"
        "When the user (coordinator agent) asks you to analyze a Python "
        "repository or file path, do the following:\n"
        "1) Call the scan_repo tool on the given path (optionally filtering "
        "for HIGH severity).\n"
        "2) Inspect the Bandit results and choose exactly ONE high severity "
        "finding to focus on. If there is no HIGH severity issue, choose one "
        "MEDIUM severity finding.\n"
        "3) Return a concise textual 'task' description for a fixer agent, "
        "including:\n"
        "   - file path\n"
        "   - line number\n"
        "   - severity\n"
        "   - Bandit test_id\n"
        "   - short issue summary\n"
        "Do NOT propose code changes yourself. Your sole job is to select and "
        "describe a single issue."
    ),
    tools=[scan_repo],
)


fixer_agent = Agent(
    model="gemini-2.5-flash",
    name="fixer_agent",
    description="StaticGuard fixer that proposes minimal patches and evaluates them.",
    instruction=(
        "You are a patching assistant for static security issues.\n"
        "You will receive a description of ONE Bandit finding (file path, line "
        "number, severity, test_id, and issue summary) plus any extra code "
        "context that the coordinator agent provides.\n\n"
        "Your job:\n"
        "1) Use the load_file_tool to load the full original file content if "
        "it is not already provided.\n"
        "2) Propose a MINIMAL patch that fixes the issue. Only modify the "
        "function or very small region that contains the problem. Avoid "
        "refactoring unrelated code.\n"
        "3) Produce:\n"
        "   a) The FULL patched file content.\n"
        "   b) A unified diff between the original and patched code.\n"
        "4) Call evaluate_patch_tool with the original file path and the FULL "
        "patched content to compute Bandit metrics before and after.\n"
        "5) Return a clear explanation that includes:\n"
        "   - the unified diff\n"
        "   - the evaluation result (original vs patched summaries, plus delta)\n"
        "If the issue is too complex or risky to auto-fix safely, clearly say "
        "so and explain why you are skipping the patch."
    ),
    tools=[load_file_tool, evaluate_patch_tool],
)
