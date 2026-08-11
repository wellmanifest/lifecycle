# Logic flow

Validation is deterministic and fail-closed. No partial model becomes valid.

```mermaid
flowchart TD
    A[Read UTF-8 document] --> B{Lexical and statement syntax valid?}
    B -- no --> E[Emit stable LFC-SYNTAX diagnostic]
    B -- yes --> C[Build declarations and transition table]
    C --> D{References, determinism and graph valid?}
    D -- no --> F[Emit stable LFC-MODEL diagnostic]
    D -- yes --> G{Reject rules bind declared errors?}
    G -- no --> H[Emit stable LFC-ERROR diagnostic]
    G -- yes --> I[Return validated lifecycle model]
    E --> J[Exit 1]
    F --> J
    H --> J
    I --> K[Exit 0 and text or JSON report]
```

The validator collects independent diagnostics in source order, then sorts the
final report by line and stable code. Unexpected internal failures use exit 2
and are never reported as a valid lifecycle.
