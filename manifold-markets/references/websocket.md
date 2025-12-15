# WebSocket Real-time Updates

Connect to `wss://api.manifold.markets/ws` for live data.

---

## Basic Usage

```python
from bayesianbot.clients.manifold.realtime import ManifoldRealtimeClient

ws = ManifoldRealtimeClient()

def on_message(msg):
    # msg = {"type": "broadcast", "topic": "...", "data": {...}}
    print(msg["topic"], msg["data"])

ws.on_broadcast = on_message
ws.start()

# Subscribe to topics
ws.subscribe([
    "global/new-bet",                          # All bets platform-wide
    f"contract/{market_id}/new-bet",           # Bets on specific market
    f"contract/{market_id}/orders",            # Limit order updates
    f"contract/{market_id}/user-metrics/{user_id}",  # Position changes
])

# Later: unsubscribe
ws.unsubscribe(["global/new-bet"])

# Cleanup
ws.stop(wait=True)
```

---

## Message Protocol

All messages are JSON with `type` and `txid`:

**Subscribe request:**
```json
{"type": "subscribe", "txid": 1, "topics": ["global/new-bet"]}
```

**Server acknowledgment:**
```json
{"type": "ack", "txid": 1, "success": true}
```

**Broadcast (incoming data):**
```json
{"type": "broadcast", "topic": "contract/abc/new-bet", "data": {...}}
```

---

## Available Topics

### Global Topics

| Topic | Description |
|-------|-------------|
| `global/new-bet` | All bets across all markets |
| `global/new-contract` | New markets created |
| `global/new-comment` | All comments |
| `global/updated-contract` | Market updates |

### Per-Contract Topics

Replace `{id}` with market ID:

| Topic | Description |
|-------|-------------|
| `contract/{id}` | General updates |
| `contract/{id}/new-bet` | Bets on this market |
| `contract/{id}/new-comment` | Comments |
| `contract/{id}/new-answer` | New answers (multi-choice) |
| `contract/{id}/updated-answers` | Answer updates |
| `contract/{id}/orders` | Limit order updates |
| `contract/{id}/user-metrics/{userId}` | Position updates for specific user |

### Other Topics

| Topic | Description |
|-------|-------------|
| `user/{userId}` | User profile updates |
| `answer/{answerId}/update` | Specific answer updates |

---

## Reconnection

`ManifoldRealtimeClient` handles reconnection automatically. On disconnect:
1. Attempts reconnect with exponential backoff
2. Re-subscribes to all previously subscribed topics
3. Calls `on_broadcast` callback when data resumes

---

## Example: Tracking Market Activity

```python
ws = ManifoldRealtimeClient()

def handle_bet(msg):
    if msg["topic"].endswith("/new-bet"):
        bet = msg["data"]
        print(f"{bet['outcome']} {bet['amount']} @ {bet['probAfter']:.1%}")

ws.on_broadcast = handle_bet
ws.start()
ws.subscribe([f"contract/{market_id}/new-bet"])

# Run until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ws.stop(wait=True)
```
