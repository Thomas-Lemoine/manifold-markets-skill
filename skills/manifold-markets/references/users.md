# Users API

User profiles, portfolios, positions, and activity tracking.

**Contents:** [Fetch Users](#fetch-users) · [Positions](#positions) · [User Contract Metrics](#user-contract-metrics) · [Portfolio](#portfolio) · [Activity](#activity) · [Loans](#loans) · [Followed Groups](#followed-groups) · [Notifications](#notifications) · [Balance History](#balance-history) · [Update Profile](#update-profile) · [Block/Unblock](#blockunblock-users) · [Achievements](#achievements) · [Notification Settings](#notification-settings)

---

## Fetch Users

### By Username or ID

```python
# Authenticated user
r = requests.get(f"{BASE}/me", headers=headers)

# By username
r = requests.get(f"{BASE}/user/{username}")

# By username - lightweight (fewer fields, faster)
r = requests.get(f"{BASE}/user/{username}/lite")

# By ID
r = requests.get(f"{BASE}/user/by-id/{user_id}")

# By ID - lightweight
r = requests.get(f"{BASE}/user/by-id/{user_id}/lite")

# Batch by IDs
r = requests.get(f"{BASE}/users/by-id",
    params=[("ids[]", id1), ("ids[]", id2)])

# Batch balances only (faster than full user objects)
r = requests.get(f"{BASE}/users/by-id/balance",
    params=[("ids[]", id1), ("ids[]", id2)])
```

### Search Users

```python
# Root path, not /v0/
r = requests.get("https://api.manifold.markets/search-users",
    params={"term": "bayesian", "limit": 10})
```

### List Users

```python
r = requests.get(f"{BASE}/users", params={
    "limit": 1000,      # Max 1000
    "before": "user_id", # Pagination cursor
})
```

### User Object

```python
{
    "id": "user123",
    "username": "someuser",
    "name": "Some User",
    "avatarUrl": "https://...",
    "bio": "About me...",

    "createdTime": 1600000000000,
    "balance": 1000.0,              # Current mana balance
    "totalDeposits": 500.0,

    "creatorTraders": {             # Unique bettors on user's markets
        "daily": 5,
        "weekly": 20,
        "monthly": 100,
        "allTime": 5000,
    },

    # Status flags
    "isBot": False,
    "isAdmin": False,
    "isTrustworthy": False,
    "isBannedFromPosting": False,

    # Activity
    "lastBetTime": 1700000000000,
    "currentBettingStreak": 5,
    "streakForgiveness": 2,

    # Loans
    "nextLoanCached": 2500.0,

    # Social
    "twitterHandle": "username",
    "discordHandle": "user#1234",
    "url": "https://manifold.markets/someuser",
}
```

---

## Positions

### Market Positions

```python
# All positions in a market
r = requests.get(f"{BASE}/market/{market_id}/positions", params={
    "order": "profit",   # profit or shares
    "top": 10,           # Top N by order
    "bottom": 5,         # Bottom N
})

# Specific user's position
r = requests.get(f"{BASE}/market/{market_id}/positions", params={
    "userId": user_id,
})
# For MC markets with userId: returns BOTH aggregate (answerId=null)
# AND per-answer positions in the array
```

### Search Positions

```python
# Root path
r = requests.get("https://api.manifold.markets/search-contract-positions",
    params={"term": "username", "contractId": market_id, "limit": 20})
```

### Position Object (Contract Metrics)

```python
{
    "contractId": "market123",
    "answerId": "answer123",        # null for binary or aggregate
    "userId": "user123",

    "invested": 500.0,              # Current investment value
    "totalAmountInvested": 1000.0,  # Total ever invested
    "totalAmountSold": 500.0,

    "totalShares": {"YES": 600.0, "NO": 0.0},
    "totalSpent": {"YES": 500.0, "NO": 0.0},

    "profit": 50.0,
    "profitPercent": 10.0,
    "payout": 550.0,                # Current value if resolved now

    "hasShares": True,
    "hasYesShares": True,
    "hasNoShares": False,
    "maxSharesOutcome": "YES",

    "loan": 4.5,
    "lastBetTime": 1700000000000,
    "lastProb": 0.55,               # null for aggregate

    # Time-based metrics
    "from": {
        "day": {"invested": ..., "profit": ..., "profitPercent": ..., "value": ...},
        "week": {...},
        "month": {...},
    },
}
```

---

## User Contract Metrics

Get all positions for a user with market data:

```python
r = requests.get(f"{BASE}/get-user-contract-metrics-with-contracts", params={
    "userId": user_id,
    "limit": 100,
    "offset": 0,
    "perAnswer": "true",    # Include per-answer breakdown for MC
    "order": "profit",      # profit or lastBetTime
})
# Returns: {"contracts": [...], "metricsByContract": {...}}
```

**Note:** With `perAnswer='true'`, returns BOTH per-answer rows AND an aggregate row with `answerId: None` for each MC market.

---

## Portfolio

### Current Portfolio

```python
r = requests.get(f"{BASE}/get-user-portfolio", params={"userId": user_id})
```

### Portfolio History

```python
r = requests.get(f"{BASE}/get-user-portfolio-history", params={
    "userId": user_id,
    "period": "monthly",  # daily, weekly, monthly, allTime
})
```

---

## Activity

### Last Active Time

```python
# Root path - fast way to check when user was last active
r = requests.get("https://api.manifold.markets/get-user-last-active-time",
    params={"userId": user_id})
# Returns: {"lastActiveTime": 1767657600000}
```

### User's Bets

```python
r = requests.get(f"{BASE}/bets", params={
    "userId": user_id,
    "limit": 1000,
})
```

### User's Comments

```python
r = requests.get(f"{BASE}/comments", params={
    "userId": user_id,
    "limit": 1000,
})
```

### User's Markets

```python
r = requests.get(f"{BASE}/markets", params={
    "userId": user_id,  # Creator ID
    "limit": 1000,
})
```

### Daily Changed Metrics

```python
# Root path - requires auth
r = requests.get("https://api.manifold.markets/get-daily-changed-metrics-and-contracts",
    params={"limit": 50}, headers=headers)
```

---

## Loans

### Check Available Loan

```python
# Root path
r = requests.get("https://api.manifold.markets/get-next-loan-amount",
    params={"userId": user_id})
# Returns: {"amount": 2409.01} or {"amount": 0}
```

### Claim Daily Loan

```python
# Root path, requires auth
r = requests.get("https://api.manifold.markets/request-loan", headers=headers)
# Returns: {"message": "Loan awarded"} or {"message": "Already awarded loan today"}
```

---

## Followed Groups

```python
r = requests.get(f"{BASE}/get-followed-groups", params={"userId": user_id})
```

---

## Notifications

```python
# Root path, requires auth
r = requests.get("https://api.manifold.markets/get-notifications",
    params={"limit": 50}, headers=headers)
```

---

## Balance History

```python
# Root path, requires auth
r = requests.get("https://api.manifold.markets/get-balance-changes",
    params={"userId": user_id}, headers=headers)
# Note: Does NOT support 'limit' param
```

---

## Update Profile

```python
r = requests.post(f"{BASE}/me/update", headers=headers, json={
    "name": "New Display Name",
    "bio": "Updated bio",
    "avatarUrl": "https://...",
    # Other updatable fields: website, twitterHandle, discordHandle
})
```

---

## Block/Unblock Users

```python
# Block a user
r = requests.post(f"{BASE}/user/by-id/{user_id}/block", headers=headers)

# Unblock a user
r = requests.post(f"{BASE}/user/by-id/{user_id}/unblock", headers=headers)
```

---

## Achievements

```python
r = requests.get(f"{BASE}/get-user-achievements", params={"userId": user_id})

# Response:
{
    "userId": "user123",

    # Trading stats
    "totalTradesCount": 5217,
    "totalVolumeMana": 2711736.86,
    "profitableMarketsCount": 1280,
    "unprofitableMarketsCount": 871,
    "largestProfitableTradeValue": 438537.0,
    "largestUnprofitableTradeValue": -115055.0,

    # Streaks
    "longestBettingStreak": 115,

    # Creator stats
    "creatorTraders": 5499,              # Unique bettors on user's markets
    "totalMarketsCreated": 210,
    "totalLiquidityCreatedMarkets": 332072.45,

    # Social/referral
    "totalReferrals": 120,
    "totalReferredProfitMana": 1856036.58,
    "numberOfComments": 1354,

    # League stats
    "seasonsPlatinumOrHigher": 27,
    "seasonsDiamondOrHigher": 13,
    "seasonsMasters": 2,
    "largestLeagueSeasonEarnings": 47481.86,

    # Other
    "accountAgeYears": 4.09,
    "modTicketsResolved": 0,
    "charityDonatedMana": 5971.03,

    # Rankings (percentile within all users)
    "ranks": {
        "creatorTraders": {"rank": 99, "percentile": 0.06},
        "totalReferrals": {"rank": 45, "percentile": 0.03},
        # ... other ranking categories
    }
}
```

---

## Performance Stats & Calibration

Get detailed performance metrics including Sharpe ratio:

```python
r = requests.get(f"{BASE}/get-user-calibration", params={"userId": user_id})

# Response:
{
    "calibration": {
        "yesPoints": [{"x": 0.1, "y": 0.08}, ...],  # Predicted vs actual for YES bets
        "noPoints": [{"x": 0.1, "y": 0.12}, ...],   # Predicted vs actual for NO bets
    },
    "performanceStats": {
        "totalProfit": 50000.0,
        "profit365": 12000.0,
        "totalVolume": 200000.0,
        "winRate": 62.5,            # PERCENTAGE, not decimal (62.5 = 62.5%)
        "totalMarkets": 600,
        "resolvedMarkets": 500,
        "volatility": 15.3,         # PERCENTAGE
        "sharpeRatio": 5.2,
        "maxDrawdown": 25.0,        # PERCENTAGE, not decimal (25.0 = 25%)
    },
    "portfolioHistory": [...],
    "profitByTopic": [              # LIST of objects, not a dict
        {
            "topic": "🤪 Fun",      # Topic name with emoji prefix
            "profit": 318601.0,     # Profit in mana (can be negative)
            "volume": 708680.0,     # Total volume traded in topic
            "marketCount": 478,     # Number of markets traded
        },
        ...
    ]
}
```

**Important:** `winRate`, `maxDrawdown`, and `volatility` are expressed as percentages, not decimals. A `winRate` of 62.5 means 62.5%, not 0.625.

**Use cases:**
- Finding top performers by Sharpe ratio
- Analyzing trading skill vs luck
- Comparing user performance metrics

**Performance note:** This endpoint recomputes stats server-side. Parallel requests queue up and don't improve throughput. For bulk operations, filter users first using fast endpoints before calling this.

---

## Notification Settings

```python
r = requests.post(f"{BASE}/update-notif-settings", headers=headers, json={
    # Settings object - check source for available options
})
