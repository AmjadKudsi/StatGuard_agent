# StatGuard_agent

```
flowchart LR
    U[Developer] --> RQ[Request<br/>- Scan repo or file<br/>- Optional fix + evaluation]

    RQ --> A[StaticGuard root agent<br/>(ADK + Gemini 2.5 Flash)]

    A --> T1[Tool: scan_repo(path, severity_filter)]
    T1 --> B[Bandit CLI<br/>static analysis only]
    B --> J[Bandit JSON result<br/>- metrics._totals<br/>- results[]]

    J --> A2[Agent explains findings<br/>- severity counts<br/>- key issues]

    A2 --> D{Patch and evaluate?}

    D -- No --> FR[Final response to developer<br/>- findings summary]

    D -- Yes --> PG[Generate minimal patch<br/>- change only function with issue<br/>- full patched file<br/>- unified diff]

    PG --> T2[Tool: evaluate_patch_tool(<br/>file_path, patched_content,<br/>severity_filter)]

    T2 --> B2[Bandit on original file<br/>Bandit on patched file]
    B2 --> EVAL[Evaluation output<br/>- original_summary<br/>- patched_summary<br/>- delta per severity]

    EVAL --> FR2[Final response to developer<br/>- diff<br/>- before/after metrics<br/>- safety assessment]

    FR --> U
    FR2 --> U
```
