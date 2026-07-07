# Traffic & Monitoring

## Traffic

```bash
dawos traffic watch              # Live traffic stream (SSE, Ctrl+C to stop)
dawos traffic watch-user USER    # Watch a specific subscriber's traffic
dawos traffic queue USER         # Show TC queue (shaper) for a subscriber
dawos traffic ratelimit USER RATE  # Apply temporary rate limit (e.g. 5M/20M)
dawos traffic ratelimit-restore USER  # Restore RADIUS-assigned rate limit
```

## Monitoring

```bash
dawos monitoring status          # Monitoring status
dawos monitoring metrics         # System metrics
dawos monitoring metrics-service # Service-level metrics
dawos monitoring configure       # Configure monitoring
dawos monitoring restart         # Restart monitoring exporters
```

Alias: `dawos mon status`, `dawos mon metrics`, etc.

## Live Dashboard

```bash
dawos top                        # Full-screen live dashboard
dawos top --interval 5           # Custom refresh interval (seconds)
```

The dashboard shows real-time session counts, throughput, and system metrics.
