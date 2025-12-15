---
name: manifold-markets
description: Comprehensive guide for exploring and programmatically interacting with Manifold Markets data. Use when implementing features that query markets, users, bets, or positions, or when analyzing prediction market data. (project)
---

# Manifold Markets API Guide

This skill teaches you how to navigate the Manifold Markets database and api programmatically using the bayesianbot codebase.

## Quick Reference

| Item | Value |
|------|-------|
| REST API | `https://api.manifold.markets/v0` |
| WebSocket | `wss://api.manifold.markets/ws` |
| Auth Header | `Authorization: Key {api_key}` |
| Rate Limit | 500 requests/minute per IP |
| **Timestamps** | **JavaScript milliseconds (NOT seconds!)** |

---

## Clients

```python
from bayesianbot.clients.manifold.client import ManifoldClient

mf = ManifoldClient()
mf.documented    # DocumentedManifoldClient - 70+ REST methods
mf.undocumented  # UndocumentedManifoldClient - experimental endpoints
mf.supabase      # SupabaseManifoldClient - bulk data access (10-100x faster)
mf.realtime      # ManifoldRealtimeClient - WebSocket for live updates
```

---

## Core Data Structures

### Market (Contract)

```python
{
    "id": "abc123",
    "slug": "will-x-happen",
    "question": "Will X happen?",
    "url": "https://manifold.markets/user/will-x-happen",
    "creatorId": "user123",
    "creatorUsername": "someuser",
    "outcomeType": "BINARY" | "MULTIPLE_CHOICE" | "PSEUDO_NUMERIC" | "POLL" | "BOUNTIED_QUESTION",
    "mechanism": "cpmm-1" | "cpmm-multi-1" | "none",
    "probability": 0.65,              # BINARY only, 0.0-1.0
    "p": 0.53,                        # AMM pool weighting parameter (see AMM section)
    "pool": {"YES": 1000.0, "NO": 500.0},
    "createdTime": 1700000000000,     # JS milliseconds!
    "closeTime": 1735689600000,       # May be null for perpetual
    "isResolved": False,
    "resolution": "YES" | "NO" | "MKT" | "CANCEL",  # Only if isResolved
    "volume": 5000.0,
    "totalLiquidity": 1000.0,
    "answers": [...],                 # MULTIPLE_CHOICE only
    "shouldAnswersSumToOne": True,    # If true, mutually exclusive
}
```

### User

```python
{
    "id": "user123",
    "username": "someuser",
    "name": "Some User",
    "balance": 1000.0,               # Current mana
    "profitCached": {"daily": 10.0, "weekly": 50.0, "monthly": 200.0, "allTime": 1500.0},
    "isBot": False,
}
```

### Bet

```python
{
    "id": "bet123",
    "userId": "user123",
    "contractId": "market123",
    "answerId": "answer123",          # Only for multi-choice
    "createdTime": 1700000000000,
    "amount": 100.0,                  # Mana spent
    "shares": 150.0,                  # Shares received
    "outcome": "YES" | "NO",
    "probBefore": 0.5,
    "probAfter": 0.55,
    # Limit orders only:
    "limitProb": 0.60,
    "isFilled": True,
    "isCancelled": False,
}
```

See [references/data-structures.md](references/data-structures.md) for full schemas including Answer and ContractMetrics.

---

## Common API Patterns

### Fetching Markets

```python
market = mf.documented.get_market_by_id("abc123")
market = mf.documented.get_market_by_slug("will-x-happen")

markets = mf.documented.search_markets(
    term="AI",
    filter="open",           # "all", "open", "closed", "resolved"
    sort="score",            # "score", "newest", "liquidity", "volume"
    contract_type="BINARY",
    limit=100,
)

# Bulk fetch (use Supabase - much faster)
for market in mf.supabase.get_all_markets_sb(after_iso="2024-01-01"):
    print(market["question"])
```

### Fetching Probabilities

```python
prob_data = mf.documented.get_market_prob("abc123")
# Returns: {"prob": 0.65} for BINARY
# Returns: {"answerProbs": {"ans1": 0.3, "ans2": 0.7}} for MULTIPLE_CHOICE

# Batch fetch (much faster for many markets)
probs = mf.documented.get_market_probs(["id1", "id2", "id3"])
```

### Fetching User Positions

```python
me = mf.documented.get_me()

metrics = mf.documented.get_user_contract_metrics_with_contracts(me["id"])

# Per-answer breakdown (CRITICAL for multi-choice!)
metrics = mf.documented.get_user_contract_metrics_with_contracts(
    me["id"],
    per_answer="true",  # String, not boolean!
)
# Returns BOTH per-answer rows AND aggregate (answerId=None) - filter accordingly
```

### Fetching Bets

```python
bets = mf.documented.get_bets(username="someuser", limit=1000)
bets = mf.documented.get_bets(contract_id="abc123")
bets = mf.documented.get_bets(user_id="user123", kinds="open-limit")
all_bets = mf.documented.get_all_bets(username="someuser")  # Generator
```

### Placing Bets

```python
from bayesianbot.clients.manifold.documented import BetParams

# Market order
result = mf.documented.place_bet(BetParams(
    contractId="abc123", amount=100, outcome="YES",
))

# Limit order (IOC pattern)
result = mf.documented.place_bet(BetParams(
    contractId="abc123", amount=100, outcome="YES",
    limitProb=0.70, expiresMillisAfter=10,
))

# Multi-choice (answerId REQUIRED)
result = mf.documented.place_bet(BetParams(
    contractId="abc123", amount=100, outcome="YES", answerId="answer123",
))

# Dry run
result = mf.documented.place_bet(BetParams(
    contractId="abc123", amount=100, outcome="YES", dryRun="true",
))
```

### Selling & Canceling

```python
mf.documented.sell_shares(market_id="abc123", outcome="YES")
mf.documented.sell_shares(market_id="abc123", outcome="YES", answer_id="answer123")
mf.documented.cancel_bet("bet123")
```

---

## Transactions

Track mana movements with `mf.documented.get_txns()`. Useful for analyzing creator earnings, tracking payouts, auditing transfers.

```python
txns = mf.documented.get_txns(to_id="user123", limit=100)
txns = mf.documented.get_txns(category="UNIQUE_BETTOR_BONUS", limit=100)
txns = mf.documented.get_txns(after=1700000000000, before=1701000000000)
```

**Common categories:**
| Category | Description |
|----------|-------------|
| `UNIQUE_BETTOR_BONUS` | Creator bonus for new bettor |
| `BETTING_STREAK_BONUS` | Daily streak reward |
| `LOAN` | Daily mana loan |
| `CONTRACT_RESOLUTION_PAYOUT` | Winnings from resolved market |
| `MANA_PAYMENT` | Direct mana transfer |
| `TIP` | Comment tip |
| `ADD_SUBSIDY` | Adding liquidity |
| `REFERRAL` | Referral bonus |

See [references/transactions.md](references/transactions.md) for full 50+ category list with data fields.

---

## Supabase (Bulk Data)

10-100x faster than REST pagination. Use for bulk analysis.

```python
for market in mf.supabase.get_all_markets_sb(after_iso="2024-01-01"):
    print(market["question"])
```

**Available tables:**
| Table | Use Case |
|-------|----------|
| `contracts` | All markets |
| `users` | All user profiles |
| `answers` | Multi-choice answers with pools |
| `user_contract_metrics` | User positions (faster than REST) |
| `user_portfolio_history` | Portfolio value over time |
| `user_follows` | Follow relationships |
| `groups` | Topic groups |
| `contract_liquidity` | Liquidity provisions |

See [references/supabase.md](references/supabase.md) for all methods and parameters.

---

## WebSocket (Real-time)

```python
from bayesianbot.clients.manifold.realtime import ManifoldRealtimeClient

ws = ManifoldRealtimeClient()
ws.on_broadcast = lambda msg: print(msg["topic"], msg["data"])
ws.start()
ws.subscribe(["global/new-bet", f"contract/{market_id}/new-bet"])
ws.stop(wait=True)
```

**Topics:** `global/new-bet`, `global/new-contract`, `contract/{id}/new-bet`, `contract/{id}/orders`, `contract/{id}/user-metrics/{userId}`

See [references/websocket.md](references/websocket.md) for full topic list and protocol.

---

## Undocumented Endpoints

**Use root path (no `/v0/`):** `https://api.manifold.markets/search-users`

| Endpoint | Description |
|----------|-------------|
| `/search-users` | Search users by name/username |
| `/get-contract` | Extended market data (more fields than /v0/market) |
| `/get-related-markets` | Find similar markets |
| `/get-next-loan-amount` | Check available daily loan |
| `/get-channel-memberships` | List DM channels |
| `/get-channel-messages` | Read DM messages |
| `/get-balance-changes` | Balance history |
| `/get-user-limit-orders-with-contracts` | Open limit orders with market data |
| `/get-daily-changed-metrics-and-contracts` | Markets with recent activity |
| `/get-mana-supply` | Platform-wide mana statistics |

See [references/undocumented.md](references/undocumented.md) for usage examples.

---

## Market Types

| Type | Description |
|------|-------------|
| `BINARY` | Simple YES/NO |
| `MULTIPLE_CHOICE` | Multiple answers |
| `PSEUDO_NUMERIC` | Continuous range |
| `POLL` | Non-tradeable poll |
| `BOUNTIED_QUESTION` | Bounty for best answer |

**For `MULTIPLE_CHOICE` with `shouldAnswersSumToOne=true`:**
- Buying YES on one answer implicitly sells others
- Use `POST /v0/multi-bet` for multi-leg bets

---

## AMM Mechanics

Manifold uses CPMM (Constant Product Market Maker) with weighting parameter `p`:

```
probability = (p * NO) / ((1 - p) * YES + p * NO)
```

Where `YES`/`NO` are pool share quantities, `p` shifts with liquidity changes.

```python
pool = {"YES": 1000, "NO": 500}
p = 0.5
prob = (0.5 * 500) / ((0.5 * 1000) + (0.5 * 500))  # = 0.333
```

Source: [calculate-cpmm.ts](https://github.com/manifoldmarkets/manifold/blob/main/common/src/calculate-cpmm.ts)

---

## Gotchas

### 1. Timestamps are JavaScript Milliseconds
```python
close_time_sec = market["closeTime"] / 1000  # Convert to seconds
```

### 2. per_answer Returns Aggregate Row Too
```python
for entry in metrics["metricsByContract"]["market123"]:
    if entry["answerId"] is None:
        continue  # Skip aggregate
```

### 3. Some Fields May Be Absent
```python
last_bet = market.get("lastBetTime")   # None if no bets
close_time = market.get("closeTime")   # None for perpetual
if market.get("isResolved"):
    print(market["resolution"])
```

### 4. String Parameters for Limit Orders
```python
params = BetParams(dryRun="true", ...)  # NOT True (boolean)
```

### 5. Rate Limits
500 requests/minute. Use `get_market_probs()` batch endpoint and Supabase for bulk.

---

## Source Code

- **API Schema**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/api/schema.ts
- **Market Math**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/calculate-cpmm.ts
- **Local clients**: `bayesianbot/clients/manifold/`
