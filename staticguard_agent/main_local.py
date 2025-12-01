# main_local.py

import sys

from agent.agent import StaticGuardAgent


def main():
    if len(sys.argv) > 1:
        # One shot mode: python main_local.py "scan /path/to/repo"
        prompt = " ".join(sys.argv[1:])
        agent = StaticGuardAgent()
        reply = agent.chat(prompt)
        print(reply)
        return

    # Simple REPL
    print("StaticGuard Agent (Step 0). Type 'scan PATH' to run stub scan, or 'quit' to exit.")
    agent = StaticGuardAgent()

    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not prompt:
            continue
        if prompt.lower() in {"quit", "exit"}:
            print("bye")
            break

        reply = agent.chat(prompt)
        print("\nagent>\n" + reply + "\n")


if __name__ == "__main__":
    main()
