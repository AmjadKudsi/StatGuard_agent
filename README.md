# StatGuard_agent

```
sequenceDiagram
    title Figure 3: StaticGuard code and runtime interactions

    participant Developer
    participant ADKCLI
    participant PythonVenv
    participant StaticGuardProcess
    participant Gemini
    participant BanditCLI
    participant LocalRepo
    participant CloudRuntime

    Developer->>ADKCLI: 1: Run "adk run staticguard_agent"
    ADKCLI->>PythonVenv: 2: Load project and dependencies
    PythonVenv->>StaticGuardProcess: 3: Start root_agent\n(staticguard_agent.agent.root_agent)

    Developer->>StaticGuardProcess: 4: Chat request\n(scan / patch file or repo)
    StaticGuardProcess->>Gemini: 5: LLM call\n(plan tools, generate text)
    Gemini-->>StaticGuardProcess: 6: Response with tool calls\nand explanations

    StaticGuardProcess->>LocalRepo: 7: Read Python files\nfor given path
    StaticGuardProcess->>BanditCLI: 8: Run "bandit -f json"\nvia run_bandit / evaluate_patch
    BanditCLI-->>StaticGuardProcess: 9: JSON findings\n(metrics, results)

    StaticGuardProcess-->>StaticGuardProcess: 10: Compute summaries\nand before/after deltas
    StaticGuardProcess-->>Developer: 11: Return findings,\npatch suggestions, metrics

    StaticGuardProcess-->>CloudRuntime: 12: (Optional) Same agent\ncan be deployed to Agent Engine\nor Cloud Run


```
