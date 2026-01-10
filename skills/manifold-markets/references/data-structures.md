# Manifold Data Structures

Complete field reference for Manifold API objects.

**Contents:** [Market](#market-contract) · [Endpoint Response Comparison](#endpoint-response-comparison) · [Market State Logic](#market-state-logic) · [Market Type Taxonomy](#market-type-taxonomy) · [Field Co-occurrence](#field-co-occurrence-patterns) · [Answer](#answer-for-multiple_choice-markets) · [User](#user) · [Bet](#bet) · [Contract Metrics](#contract-metrics-position) · [Source Code](#source-code-reference)

---

## Market (Contract)

Markets are internally called "contracts".

```python
{
    # Identity
    "id": "abc123",                    # Unique market ID
    "slug": "will-x-happen",           # URL-friendly slug
    "question": "Will X happen?",
    "url": "https://manifold.markets/user/will-x-happen",

    # Creator
    "creatorId": "user123",
    "creatorUsername": "someuser",

    # Type & Mechanism
    "outcomeType": "BINARY" | "MULTIPLE_CHOICE" | "PSEUDO_NUMERIC" | "POLL" | "BOUNTIED_QUESTION",
    "mechanism": "cpmm-1" | "cpmm-multi-1" | "none",

    # Probability (BINARY only)
    "probability": 0.65,               # Current probability 0.0-1.0
    "p": 0.53,                         # AMM pool weighting parameter

    # Pool (BINARY cpmm-1)
    "pool": {"YES": 1000.0, "NO": 500.0},

    # Timing (ALL IN MILLISECONDS!)
    "createdTime": 1700000000000,
    "closeTime": 1735689600000,        # When betting closes (may be null)
    "lastUpdatedTime": 1700100000000,
    "lastBetTime": 1700050000000,      # May be absent if no bets

    # Resolution (see Resolution Options section for full details)
    "isResolved": False,               # True when market is resolved
    "resolution": "YES" | "NO" | "MKT" | "CANCEL" | "<answer_id>",
    "resolutionTime": 1735700000000,   # When resolved
    "resolutionProbability": 0.75,     # Binary only; MC uses answer.resolutionProbability
    "resolverId": "user123",           # Who resolved it

    # Metrics
    "volume": 5000.0,
    "volume24Hours": 100.0,
    "totalLiquidity": 1000.0,
    "uniqueBettorCount": 42,

    # Multi-choice specific
    "answers": [...],                  # List of Answer objects
    "shouldAnswersSumToOne": True,     # If true, answers are mutually exclusive

    # Visibility
    "visibility": "public" | "unlisted",
}
```

---

## Endpoint Response Comparison

Different endpoints return different subsets of fields. This matters when you need specific data.

### Fields by Endpoint

| Field | `/search-markets` | `/markets` | `/market/{id}` | Supabase |
|-------|:-----------------:|:----------:|:--------------:|:--------:|
| `id`, `slug`, `question` | ✓ | ✓ | ✓ | ✓ |
| `creatorId`, `creatorUsername` | ✓ | ✓ | ✓ | ✓ (data) |
| `outcomeType`, `mechanism` | ✓ | ✓ | ✓ | ✓ |
| `volume`, `volume24Hours` | ✓ | ✓ | ✓ | ✓ (data) |
| `totalLiquidity` | ✓ | ✓ | ✓ | ✓ (data) |
| `uniqueBettorCount` | ✓ | ✓ | ✓ | ✓ (data) |
| `probability`, `p`, `pool` | ✗ | ✓ | ✓ | ✓ (data) |
| `answers` | ✗ | ✗ | ✓ | via join |
| `description`, `textDescription` | ✗ | ✗ | ✓ | ✓ (data) |
| `shouldAnswersSumToOne` | ✗ | ✗ | ✓ | ✓ (data) |
| `groupSlugs` | ✗ | ✗ | ✓ | via join |
| `lastCommentTime` | ✓ | ✗ | ✓ | ✓ |
| `token` | ✓ | ✗ | ✓ | ✗ |

### When to Use Each Endpoint

| Need | Best Endpoint |
|------|---------------|
| Search by keyword | `/search-markets` |
| Recent activity | `/markets` with `sort=last-bet-time` |
| Full market details | `/market/{id}` |
| MC answers & pools | `/market/{id}` (includes `answers`) |
| Top by all-time volume | **Supabase** (REST has no volume sort) |
| Bulk fetch (1000+) | **Supabase** (pagination built-in) |
| Sorting by JSON fields | **Supabase** (`order("data->field")`) |

### Sort Options by Endpoint

| Endpoint | Sort Options |
|----------|--------------|
| `/markets` | `created-time`, `updated-time`, `last-bet-time`, `last-comment-time` |
| `/search-markets` | `score`, `newest`, `daily-score`, `freshness-score`, `24-hour-vol`, `most-popular`, `liquidity`, `subsidy`, `last-updated`, `close-date`, `start-time`, `resolve-date`, `random`, `bounty-amount`, `prob-descending`, `prob-ascending` |
| Supabase | Any column, including `data->volume`, `data->prob`, etc. |

**Note:** There is NO `volume` sort in REST. Use Supabase for all-time volume ranking.

---

## Market State Logic

From Manifold's `tradingAllowed()` function:

```python
def trading_allowed(contract, answer=None):
    """Check if trading is permitted on this market/answer."""
    return (
        not contract.get("isResolved") and
        (not contract.get("closeTime") or contract["closeTime"] > time.time() * 1000) and
        contract.get("mechanism") != "none" and
        (answer is None or not answer.get("resolution"))
    )
```

**Market States:**

| State | Conditions | Can Bet? |
|-------|------------|----------|
| **Open** | `isResolved=False`, `closeTime > now` (or null) | ✓ Yes |
| **Closed** | `isResolved=False`, `closeTime < now` | ✗ No |
| **Resolved** | `isResolved=True` | ✗ No |
| **No mechanism** | `mechanism="none"` (polls, bounties) | ✗ No |

**Special case - Individual answer resolution:**
For unlinked multi-choice markets (`shouldAnswersSumToOne=False`), individual answers can be resolved while the market remains open. Check `answer["resolution"]` before betting on specific answers.

---

## Market Type Taxonomy

### Outcome Types

| Type | Mechanism | Description |
|------|-----------|-------------|
| `BINARY` | `cpmm-1` | YES/NO market, variable `p` parameter |
| `MULTIPLE_CHOICE` | `cpmm-multi-1` | Multiple answers, always `p=0.5` |
| `PSEUDO_NUMERIC` | `cpmm-1` | Numeric range mapped to 0-1 probability |
| `STONK` | `cpmm-1` | Stock-like market (similar to binary) |
| `NUMBER` | `cpmm-multi-1` | Numeric with discrete buckets |
| `MULTI_NUMERIC` | varies | Multi-dimensional numeric |
| `DATE` | varies | Date prediction market |
| `POLL` | `none` | Non-tradeable voting |
| `BOUNTIED_QUESTION` | `none` | Bounty for best answer |

### Mechanisms

| Mechanism | Markets | Pool Parameter | Notes |
|-----------|---------|----------------|-------|
| `cpmm-1` | BINARY, PSEUDO_NUMERIC, STONK | Variable `p` | Standard CPMM |
| `cpmm-multi-1` | MULTIPLE_CHOICE, NUMBER | Fixed `p=0.5` | Always use closed-form |
| `none` | POLL, BOUNTIED_QUESTION | N/A | No trading |

### Linked vs Unlinked Multi-Choice

**`shouldAnswersSumToOne`** is the critical field:

| Value | Behavior | Individual Resolution | Example |
|-------|----------|----------------------|---------|
| `False` | Each answer independent | ✓ Allowed | "Will X IPO in 2026?" (each company separate) |
| `True` | Mutually exclusive | ✗ Not allowed | "Who wins the election?" (only one winner) |

For linked markets, buying YES on one answer triggers automatic arbitrage across all answers to maintain sum = 1.

---

## Field Co-occurrence Patterns

### Always Present
- `id`, `slug`, `question`, `outcomeType`, `mechanism`
- `createdTime`, `creatorId`, `creatorUsername`

### Conditional Fields

| Field | Present When |
|-------|--------------|
| `probability` | `outcomeType` is BINARY or PSEUDO_NUMERIC |
| `p` | `mechanism` is `cpmm-1` |
| `pool` | `mechanism` is `cpmm-1` |
| `answers` | `outcomeType` is MULTIPLE_CHOICE or NUMBER |
| `shouldAnswersSumToOne` | `outcomeType` is MULTIPLE_CHOICE |
| `closeTime` | Market has deadline (null for perpetual, polls, bounties) |
| `resolution` | `isResolved` is True |
| `resolutionTime` | `isResolved` is True |
| `resolutionProbability` | Binary resolved, or answer in resolved MC |
| `min`, `max` | PSEUDO_NUMERIC or NUMBER markets |
| `isLogScale` | PSEUDO_NUMERIC markets |

### Answer-Specific Fields

| Field | Present When |
|-------|--------------|
| `answerId` | Multi-choice bet or position |
| `answer.resolution` | Individual answer resolved (unlinked MC only) |
| `answer.resolutionTime` | Individual answer resolved |
| `answer.resolutionProbability` | When market or answer resolved |

### Resolution Options

**Binary markets:**

| `resolution` | Meaning | `resolutionProbability` |
|--------------|---------|-------------------------|
| `"YES"` | Resolves YES | ~0.99 (final prob) |
| `"NO"` | Resolves NO | ~0.01 (final prob) |
| `"MKT"` | Partial/probability resolution | Custom 0-1 value |
| `"CANCEL"` | Market cancelled, refunds all | Final prob at cancel |

**Linked MC (`shouldAnswersSumToOne=True`):**

| `resolution` | Meaning | Market `resolutionProbability` |
|--------------|---------|-------------------------------|
| `<answer_id>` | Single winner | `None` (check answers) |
| `"MKT"` or `"CHOOSE_MULTIPLE"` | Probability split | `None` (check answers) |
| `"CANCEL"` | Market cancelled | N/A |

**Important:** For linked MC, market-level `resolutionProbability` is always `None`. Check individual `answer.resolutionProbability` values (they sum to 1).

Example single winner:
```python
{
    "resolution": "abc123",           # winning answer ID
    "resolutionProbability": None,    # always None for MC!
    "answers": [
        {"id": "abc123", "resolutionProbability": 0.998},  # winner
        {"id": "def456", "resolutionProbability": 0.001},
        {"id": "ghi789", "resolutionProbability": 0.001},
    ]
}  # answer probs sum to 1.0
```

Example probability split (MKT/CHOOSE_MULTIPLE):
```python
{
    "resolution": "CHOOSE_MULTIPLE",  # or "MKT"
    "resolutionProbability": None,
    "answers": [
        {"id": "abc123", "resolutionProbability": 0.60},
        {"id": "def456", "resolutionProbability": 0.40},
    ]
}  # sum = 1.0
```

**Unlinked MC (`shouldAnswersSumToOne=False`):**
- Market may remain unresolved (`isResolved=False`) while individual answers resolve
- Each answer resolves independently: `"YES"`, `"NO"`, `"MKT"`, or `"CANCEL"`
- Individual `resolutionProbability` values do NOT need to sum to 1
- Can bet on unresolved answers while market is open

Example:
```python
{"isResolved": false, "answers": [
    {"resolution": "NO", "resolutionProbability": 0.01},   # resolved
    {"resolution": "YES", "resolutionProbability": 0.95},  # resolved
    {"resolution": null},  # still open for betting
]}
```

---

## Answer (for MULTIPLE_CHOICE markets)

```python
{
    "id": "answer123",
    "contractId": "market123",
    "text": "Option A",
    "index": 0,                        # Display order
    "userId": "user123",               # Who created this answer
    "createdTime": 1700000000000,

    # Pool (nested format in market["answers"])
    "pool": {"YES": 500.0, "NO": 500.0},
    "prob": 0.5,
    "probability": 0.5,                # Same as prob

    # Note: All MC markets use p=0.5 (hardcoded)
    # prob = pool["NO"] / (pool["YES"] + pool["NO"])

    # Resolution (unlinked MC only, or after market resolution)
    "resolution": "YES" | "NO",        # Only for unlinked MC
    "resolutionTime": 1735700000000,
    "resolutionProbability": 0.99,     # Payout ratio

    # Metrics
    "volume": 1000.0,
    "totalLiquidity": 200.0,
    "subsidyPool": 0,

    # Optional
    "isOther": False,                  # True for "Other" catch-all answer
    "probChanges": {
        "day": 0.01,
        "week": -0.02,
        "month": 0.05,
    },
}
```

**Pool format note:** In `market["answers"]`, pools use nested `pool: {"YES": ..., "NO": ...}`. Supabase uses flat `pool_yes`/`pool_no` columns.

**Market-level MC fields:**
- `addAnswersMode`: `"DISABLED"` | `"ONLY_CREATOR"` | `"ANYONE"` - who can add answers
- `shouldAnswersSumToOne`: `true` (linked) | `false` (unlinked)

---

## User

```python
{
    "id": "user123",
    "username": "someuser",
    "name": "Some User",
    "avatarUrl": "https://...",

    "createdTime": 1600000000000,
    "balance": 1000.0,                 # Current mana balance
    "totalDeposits": 500.0,

    "isBot": False,
    "isAdmin": False,
    "isBannedFromPosting": False,

    "lastBetTime": 1700000000000,      # May be absent
    "currentBettingStreak": 5,
}
```

---

## Bet

```python
{
    "id": "bet123",
    "userId": "user123",
    "contractId": "market123",
    "answerId": "answer123",           # Only for multi-choice

    "createdTime": 1700000000000,
    "amount": 100.0,                   # Mana spent
    "shares": 150.0,                   # Shares received
    "outcome": "YES" | "NO",

    "probBefore": 0.5,
    "probAfter": 0.55,

    # Limit order fields (if applicable)
    "limitProb": 0.60,                 # Only for limit orders
    "orderAmount": 100.0,              # Original order size
    "isFilled": True,
    "isCancelled": False,
    "fills": [...],                    # Partial fill history
    "expiresAt": 1700100000000,

    # Metadata
    "isApi": True,                     # Placed via API
    "isRedemption": False,             # Automatic share redemption
    "loanAmount": 0.0,
    "fees": {"creatorFee": 0, "platformFee": 0, "liquidityFee": 0},
}
```

---

## Contract Metrics (Position)

Returned by `get_user_contract_metrics_with_contracts`:

```python
{
    "contractId": "market123",
    "answerId": "answer123",           # null for aggregate or BINARY
    "userId": "user123",

    "invested": 500.0,                 # Current investment
    "totalAmountInvested": 1000.0,     # Total ever invested
    "totalAmountSold": 500.0,

    "totalShares": {"YES": 600.0, "NO": 0.0},
    "totalSpent": {"YES": 500.0, "NO": 0.0},

    "profit": 50.0,
    "profitPercent": 10.0,
    "payout": 550.0,                   # Current value if sold

    "hasShares": True,
    "hasYesShares": True,
    "hasNoShares": False,
    "maxSharesOutcome": "YES",

    "loan": 4.5,
    "lastBetTime": 1700000000000,
    "lastProb": 0.55,                  # null for aggregate

    # Time-based metrics
    "from": {
        "day": {"invested": ..., "profit": ..., "profitPercent": ..., "value": ..., "prevValue": ...},
        "week": {...},
        "month": {...},
    },
}
```

**Note**: With `per_answer='true'`, returns BOTH per-answer rows AND an aggregate row with `answerId: None`.

---

## Source Code Reference

- **Contract types**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/contract.ts
- **Bet types**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/bet.ts
- **User types**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/user.ts
- **Answer types**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/answer.ts
- **API schema**: https://github.com/manifoldmarkets/manifold/blob/main/common/src/api/schema.ts
