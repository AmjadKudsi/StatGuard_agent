from google.adk.agents.llm_agent import Agent
from google.adk.tools.function_tool import FunctionTool

from .agent.tools import run_bandit_stub
from .agent.reporting import build_basic_report


def scan_repo(repo_path: str) -> str:
    """
    Tool: Scan a Python repo or single file path with Bandit (stub for Step 0)
    and return a markdown report string.

    In Step 1, run_bandit_stub will be replaced with a real Bandit JSON call.
    """
    bandit_result = run_bandit_stub(repo_path)
    report = build_basic_report(bandit_result)
    return report


# Wrap the Python function as an ADK FunctionTool
scan_repo_tool = FunctionTool.from_defaults(
    fn=scan_repo,
    name="scan_repo",
    description=(
        "Run a static security scan (currently a stub) on a given "
        "Python repository or file path and return a markdown report."
    ),
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="staticguard_root",
    description=(
        "StaticGuard: a non-executing static security assistant for Python code."
    ),
    instruction=(
        "You are StaticGuard, an assistant that helps users run and interpret "
        "static security scans for Python code. "
        "Use the scan_repo tool when the user asks you to scan a path. "
        "Never claim to have executed any code or tests."
    ),
    tools=[scan_repo_tool],
)
