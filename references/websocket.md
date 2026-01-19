# WebSocket Real-time Updates

Connect to `wss://api.manifold.markets/ws` for live data.

**Contents:** [Protocol](#protocol) · [Basic Usage](#basic-usage) · [Message Formats](#message-formats) · [Available Topics](#available-topics) · [Payload Examples](#broadcast-payload-examples) · [Keep-Alive](#keep-alive) · [Full Example](#full-example-with-reconnect) · [Notes](#notes)

---

## Protocol

Manifold uses a simple JSON message protocol (NOT Phoenix channels).

**Message types:**
- `subscribe` - Subscribe to topics
- `unsubscribe` - Unsubscribe from topics
- `ping` - Keep connection alive
- `ack` - Server acknowledgment
- `broadcast` - Server pushing data

---

## Basic Usage

```python
import json
import websocket

def on_message(ws, message):
    msg = json.loads(message)

    if msg["type"] == "ack":
        print(f"Subscribed: {msg['success']}")
    elif msg["type"] == "broadcast":
        topic = msg["topic"]
        data = msg["data"]
        print(f"Topic: {topic}, Data: {data}")

def on_open(ws):
    # Subscribe to topics
    ws.send(json.dumps({
        "type": "subscribe",
        "txid": 1,
        "topics": ["global/new-bet", "contract/ABC123/new-bet"]
    }))

ws = websocket.WebSocketApp(
    "wss://api.manifold.markets/ws",
    on_open=on_open,
    on_message=on_message,
)
ws.run_forever()
```

---

## Message Formats

### Subscribe

```json
{
  "type": "subscribe",
  "txid": 1,
  "topics": ["global/new-bet", "contract/{marketId}/new-bet"]
}
```

### Unsubscribe

```json
{
  "type": "unsubscribe",
  "txid": 2,
  "topics": ["global/new-bet"]
}
```

### Ping (keep-alive)

```json
{
  "type": "ping",
  "txid": 3
}
```

### Server Ack

```json
{
  "type": "ack",
  "txid": 1,
  "success": true
}
```

### Broadcast (server → client)

```json
{
  "type": "broadcast",
  "topic": "global/new-bet",
  "data": {
    "bets": [...]
  }
}
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

## Broadcast Payload Examples

### global/new-bet

```json
{
  "bets": [{
    "id": "bet123",
    "userId": "user123",
    "contractId": "market123",
    "amount": 100,
    "shares": 150,
    "outcome": "YES",
    "probBefore": 0.5,
    "probAfter": 0.55,
    "createdTime": 1700000000000,
    "isApi": false,
    "orderAmount": 100
  }]
}
```

### contract/{id}/orders

```json
{
  "id": "bet123",
  "limitProb": 0.60,
  "orderAmount": 100,
  "amount": 50,
  "isFilled": false,
  "isCancelled": false
}
```

---

## Keep-Alive

Send ping every 30 seconds to prevent disconnection:

```python
import threading
import time

def heartbeat(ws):
    txid = 1000
    while ws.sock and ws.sock.connected:
        txid += 1
        ws.send(json.dumps({"type": "ping", "txid": txid}))
        time.sleep(30)

# Start after connection
threading.Thread(target=heartbeat, args=(ws,), daemon=True).start()
```

---

## Full Example with Reconnect

```python
import json
import threading
import time
from websocket import WebSocketApp

class ManifoldWS:
    def __init__(self, topics: list[str]):
        self.topics = topics
        self.ws = None
        self.txid = 0

    def _next_txid(self):
        self.txid += 1
        return self.txid

    def on_message(self, ws, message):
        msg = json.loads(message)
        if msg["type"] == "broadcast":
            print(f"[{msg['topic']}] {msg['data']}")

    def on_open(self, ws):
        # Subscribe to all topics
        ws.send(json.dumps({
            "type": "subscribe",
            "txid": self._next_txid(),
            "topics": self.topics
        }))
        # Start heartbeat
        threading.Thread(target=self._heartbeat, daemon=True).start()

    def _heartbeat(self):
        while self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps({
                "type": "ping",
                "txid": self._next_txid()
            }))
            time.sleep(30)

    def run_forever(self):
        while True:
            try:
                self.ws = WebSocketApp(
                    "wss://api.manifold.markets/ws",
                    on_open=self.on_open,
                    on_message=self.on_message,
                )
                self.ws.run_forever()
            except Exception as e:
                print(f"Disconnected: {e}")
            time.sleep(5)  # Reconnect delay

# Usage
ws = ManifoldWS(["global/new-bet", "contract/ABC123/new-bet"])
ws.run_forever()
```

---

## Notes

- No authentication required for public topics
- Subscribe to specific markets rather than `global/*` when possible (lower volume)
- `txid` is optional but useful for tracking acks
- Broadcasts include full bet/comment objects, not just IDs
