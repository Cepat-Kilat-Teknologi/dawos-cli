# Session Management

Manage PPPoE sessions on your BNG router.

## Commands

### List Sessions

```bash
dawos session list
```

Shows all active PPPoE sessions with username, IP, rate limit, type, state, and uptime.

### Find Session

```bash
dawos session find <username>
```

Search for a specific subscriber's active session.

### Session Statistics

```bash
dawos session stats
```

### Terminate Session

```bash
dawos session terminate <username>
dawos session terminate <username> --force  # skip confirmation
```

### Restart Session

```bash
dawos session restart <username>
```

Drop and reconnect a subscriber's session.

### Lookup by SID / IP / MAC

```bash
dawos session by-sid <session-id>
dawos session by-ip <ip-address>
dawos session drop-by-mac <mac-address>
```

### Session Snapshot

```bash
dawos session snapshot <username>
```

Get a detailed snapshot of a subscriber's session including traffic counters.
