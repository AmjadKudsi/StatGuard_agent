# StaticGuard: Static Security Patch Assistant for Python

StaticGuard is a small multi agent system that performs static only security review and patch evaluation for Python code. It never executes the target program. Instead, it uses Bandit for static analysis, proposes minimal patches with a Gemini model, and then reruns Bandit on the patched version to measure how the static findings change.

This project was built as part of the 5 Day AI Agents Intensive (Google x Kaggle) and is designed to be both a useful tool for real code and a concrete instantiation of a static only code security agent for research.

## Features

* Static only security analysis for Python using Bandit.
* Multi agent design:

  * scanner agent: triages Bandit findings and selects one issue to focus on.
  * fixer agent: proposes a minimal patch and evaluates it.
  * coordinator agent: orchestrates a single scan and fix pass.
* Tools:

  * `run_bandit` wrapper for Bandit in JSON mode.
  * `evaluate_patch` that runs Bandit on original and patched code and computes severity deltas.
  * `load_file` to read code without executing it.
  * `build_markdown_report` to render a compact evaluation report with metrics and a diff.
* Sessions and memory:

  * `InMemorySessionService` for per run sessions.
  * `InMemoryMemoryService` to store a short summary of each run and make it searchable.
* Evaluation focused:

  * The system explicitly reports whether a patch reduced high severity findings, left them unchanged, or introduced new issues.

## Repository layout

```
staticguard_agent/
  agent.py           # root_agent coordinator, scanner and fixer tools
  sub_agents.py      # scanner_agent and fixer_agent definitions
  sglib/
    __init__.py
    tools.py         # run_bandit, evaluate_patch, load_file
    reporting.py     # build_markdown_report
  main_local.py      # CLI runner using Runner + sessions + memory
tests/
  test_tools.py      # small tests for run_bandit and evaluate_patch
requirements.txt
README.md
.env.example
```

`sglib` is a helper package for tools and reporting. `staticguard_agent.agent` exposes `root_agent`, which is the entry point for both the CLI and the ADK web UI.

## Setup

1. Clone the repository and create a virtual environment:

```bash
git clone [https://github.com/](https://github.com/)<your-user>/staticguard-agent.git
cd staticguard-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate ```

2. Install dependencies:

```bash
pip install -r requirements.txt ```

3. Configure your Gemini API key. Create `.env` in the project root or in `staticguard_agent/`:

```text
GOOGLE_API_KEY=your_api_key_here ```

You can get an API key from Google AI Studio.

## How to run StaticGuard

### 1. Local CLI (with sessions and memory)

The simplest entry point is the CLI in `main_local.py`:

```bash
source .venv/bin/activate
python -m staticguard_agent.main_local ```

You will be prompted for a path to scan:

```text
Path to repo or file to scan: /tmp/bandit_demo/demo.py ```

StaticGuard will:

* run the multi agent pipeline (scanner, fixer, coordinator).
* print a markdown report that includes:

  * Bandit findings before and after the patch, by severity.
  * a conclusion about whether the patch improved the situation.
  * the diff for the proposed patch.
* store a short `run_summary` in an in memory session and add the session to `InMemoryMemoryService`, then perform a sample memory search by path.

This demonstrates the use of `Runner`, `InMemorySessionService`, and `InMemoryMemoryService` in a small local application.

### 2. ADK REPL

You can also run the agent in a simple REPL using `adk run`:

```bash
source .venv/bin/activate
adk run staticguard_agent ```

This loads `root_agent` and lets you interact with it in the terminal. Example prompt:

```text
staticguard_root> Perform a single scan-and-fix pass on /tmp/bandit_demo/demo.py.
Use the scanner agent to pick one high severity issue, then use the fixer agent
to propose a minimal patch and evaluate it. Return the markdown report. ```

### 3. ADK web UI

For a browser based UI, use the ADK dev web server from the project root:

```bash
source .venv/bin/activate
adk web . ```

Then open:

```text
[http://127.0.0.1:8000](http://127.0.0.1:8000) ```

In the dev UI:

1. Select the app `staticguard_agent` (do not select `sglib`).
2. Start a new session.
3. Send a message such as:

```text
Perform a single scan-and-fix pass on /tmp/bandit_demo/demo.py.
Use the scanner agent to pick one high severity (or medium if no high)
Bandit finding, then use the fixer agent to propose a minimal patch and
evaluate it. Return the markdown report. ```

You will see the full report rendered as the assistant response. This is a simple UI for the capstone demo and screenshots.

## Example vulnerable file

To try StaticGuard on a small but realistic issue, create:

```bash
mkdir -p /tmp/bandit_demo
cat > /tmp/bandit_demo/demo.py << 'EOF'
import subprocess

def bad():
cmd = "ls " + input("Enter path: ")
subprocess.call(cmd, shell=True)
EOF ```

This snippet contains a classic `subprocess` issue that Bandit flags (user controlled input combined with `shell=True`). StaticGuard should:

* detect the Bandit finding.
* propose a patch that removes `shell=True` and uses an argument list.
* show how high severity issues change before and after the patch.

The tests in `tests/test_tools.py` use a related pattern so that readers can see the behavior of `run_bandit` and `evaluate_patch` in isolation.

## Running tests

To run the small unit tests for the core tools:

```bash
pip install pytest
pytest ```

The tests cover:

* `run_bandit` on a safe file (no findings expected).
* `run_bandit` on a subprocess shell example (findings expected).
* `evaluate_patch` on a vulnerable and patched pair (high severity should not increase after the patch).

## Deployment

### Local deployment with ADK web UI

The project is packaged as an ADK agent (`staticguard_agent`) and can be run through the ADK dev web UI using:

```bash
adk web . ```

This starts a local web server where you can select the `staticguard_agent` app and interact with StaticGuard through a browser. This serves as the primary UI for the capstone demonstration and does not require additional infrastructure.

### Cloud deployment path (Vertex AI Agent Engine)

StaticGuard can be deployed to Vertex AI Agent Engine using `adk deploy`. A possible flow:

```bash
export GOOGLE_CLOUD_PROJECT=<your-project-id>
export GOOGLE_CLOUD_REGION=us-central1

adk deploy staticguard_agent ```

This publishes the same `root_agent` used in local development to a managed runtime with observability and scaling. Whether this is free depends on your Google Cloud account and current pricing. You should check your billing information and quotas before deploying.

## Limitations and safety notes

* StaticGuard does not execute the target program. All analysis is static and based on Bandit and file reads.
* The agent does not have any tool that can create or modify files in user repositories. It only writes temporary files inside `evaluate_patch` to rerun Bandit on patched content.
* The agent is instructed not to claim that it created or saved files. It only proposes patches as text and leaves application of those patches to the user.
* The evaluation is based on Bandit’s rule set and severities. A decrease in high severity findings is a positive signal, but developers should still review patches and the full report before accepting changes.