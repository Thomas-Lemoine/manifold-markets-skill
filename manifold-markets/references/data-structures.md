# Manifold Data Structures

Complete field reference for Manifold API objects.

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

    # Resolution
    "isResolved": False,               # Present and True if resolved
    "resolution": "YES" | "NO" | "MKT" | "CANCEL",  # Only if resolved
    "resolutionTime": 1735700000000,   # Only if resolved
    "resolutionProbability": 0.75,     # Only for MKT resolution

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

**Market States:**
- **Open**: `closeTime` in future, `isResolved` absent or False
- **Closed (not resolved)**: `closeTime` in past, `isResolved` False
- **Resolved**: `isResolved` is True, has `resolution` field

---

## Answer (for MULTIPLE_CHOICE markets)

```python
{
    "id": "answer123",
    "contractId": "market123",
    "text": "Option A",
    "index": 0,                        # Display order

    # Pool-based probability
    "poolYes": 500.0,
    "poolNo": 500.0,
    "prob": 0.5,

    # Resolution (if resolved)
    "resolution": "YES" | "NO",
    "resolutionTime": 1735700000000,

    # Metrics
    "volume": 1000.0,
    "totalLiquidity": 200.0,
}
```

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

    "profitCached": {
        "daily": 10.0,
        "weekly": 50.0,
        "monthly": 200.0,
        "allTime": 1500.0,
    },

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
