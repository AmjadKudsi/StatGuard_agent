from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import uuid4

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types

from staticguard_agent.agent import root_agent

from pathlib import Path


APP_NAME = "staticguard_cli"
USER_ID = "local_user"


async def run_once(path: str) -> None:
    """Run a single scan-and-fix pass and store a compact memory entry."""

    # 1. Set up session and memory services (in-memory, dev friendly).
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    # 2. Create the Runner that ties agent + sessions + memory together.
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # 3. Create a fresh session id for this run.
    session_id = str(uuid4())
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    # 4. Build the user message that kicks off the full pipeline.
    prompt = (
        f"Perform a single scan-and-fix pass on {path}. "
        "Use the scanner agent to pick one high severity (or medium if no high) "
        "Bandit finding, then use the fixer agent to propose a minimal patch "
        "and evaluate it. Return the diff and the before/after Bandit metrics."
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    # 5. Run the agent once and capture the final response text.
    final_text = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=user_msg,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    print("\n=== StaticGuard report ===\n")
    print(final_text)

    # 6. Retrieve the completed session object.
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )

    # 7. Attach a compact summary to the session state.
    #    (Later you can parse final_text to fill in exact counts.)
    session.state["run_summary"] = {
        "path": path,
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds"),
        # placeholders for now; Step 5 will parse the real numbers
        "bandit_findings_before": "unknown",
        "bandit_findings_after": "unknown",
        "patch_attempted": True,
    }

    # 8. Add the session to the long-term memory store.
    await memory_service.add_session_to_memory(session)
    print("\n[debug] Session added to InMemoryMemoryService")

    # 9. Optional: prove memory works by searching it immediately.
    search_result = await memory_service.search_memory(
        app_name=APP_NAME,
        user_id=USER_ID,
        query=path,
    )

    print("\n[debug] Memory search results (first few entries):")
    for i, mem in enumerate(search_result.memories[:3], start=1):
        if mem.content and mem.content.parts:
            print(f"  {i}.", mem.content.parts[0].text)


async def main() -> None:
    path = input("Path to repo or file to scan: ").strip()
    if not path:
        print("No path provided, exiting.")
        return

    p = Path(path)
    if not p.exists():
        print(f"Path does not exist: {path}")
        return

    await run_once(path)



if __name__ == "__main__":
    asyncio.run(main())