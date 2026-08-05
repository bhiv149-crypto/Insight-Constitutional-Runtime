# Runtime Architecture

```
               Constitutional Runtime

                        │

                        ▼

            Platform Capability SDK

                        │

        ┌───────────────┼───────────────┐

        ▼               ▼               ▼

 Platform Registry   Replay      Observability

        │               │               │

        └───────────────┼───────────────┘

                        ▼

             Platform Runtime Adapter

                        │

        ┌───────────────┼───────────────┐

        ▼               ▼               ▼

  InsightFlow     InsightBridge    InsightCore
```

The Insight Runtime consumes Platform Runtime services exclusively
through adapter abstractions.

No Platform-owned functionality is duplicated.