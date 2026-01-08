# Betting API

Place bets, limit orders, sell positions, and manage orders.

**Contents:** [Place Bet](#place-bet) · [Multi-Bet](#multi-bet-linked-mc-markets) · [Cancel Limit Order](#cancel-limit-order) · [Sell Shares](#sell-shares) · [Get Bets](#get-bets) · [Probability History](#probability-history) · [Bet Sizing Formulas](#bet-sizing-formulas)

---

## Place Bet

### Market Order

```python
r = requests.post(f"{BASE}/bet", headers=headers, json={
    "contractId": market_id,
    "amount": 100,           # Mana to spend
    "outcome": "YES",        # YES or NO
})
```

### Limit Order

```python
r = requests.post(f"{BASE}/bet", headers=headers, json={
    "contractId": market_id,
    "amount": 100,
    "outcome": "YES",
    "limitProb": 0.60,       # Max price willing to pay (0.0-1.0)
})
```

### Immediate-or-Cancel (IOC) Order

For quick fills without leaving resting orders:

```python
r = requests.post(f"{BASE}/bet", headers=headers, json={
    "contractId": market_id,
    "amount": 100,
    "outcome": "YES",
    "limitProb": 0.60,
    "expiresMillisAfter": 10,  # Expires 10ms after placement
})
```

### Multiple Choice Markets

MC markets require `answerId`:

```python
r = requests.post(f"{BASE}/bet", headers=headers, json={
    "contractId": market_id,
    "answerId": answer_id,   # REQUIRED for MC
    "amount": 100,
    "outcome": "YES",
})
```

### Dry Run (Validate Without Executing)

```python
r = requests.post(f"{BASE}/bet", headers=headers, json={
    "contractId": market_id,
    "amount": 100,
    "outcome": "YES",
    "dryRun": "true",        # String, not boolean!
})
# Returns what would happen without placing the bet
```

### Bet Response

```python
{
    "betId": "bet123",
    "amount": 100,                    # Mana spent
    "shares": 150.5,                  # Shares received
    "outcome": "YES",
    "probBefore": 0.50,
    "probAfter": 0.55,
    "orderAmount": 100,               # Original order size (limit orders)
    "isFilled": True,                 # Fully filled?
    "fills": [                        # Partial fill details
        {
            "amount": 100,
            "shares": 150.5,
            "timestamp": 1700000000000,
            "matchedBetId": "bet456",  # If filled against limit order
        }
    ],
    "fees": {
        "creatorFee": 0,
        "platformFee": 0,
        "liquidityFee": 0,
    }
}
```

---

## Multi-Bet (Linked MC Markets)

For "sums-to-one" multiple choice markets, bet on multiple answers at once:

```python
r = requests.post(f"{BASE}/multi-bet", headers=headers, json={
    "contractId": market_id,
    "answerIds": ["ans1", "ans2"],    # Answers to buy YES on
    "amount": 100,                     # Total mana to spend
    "limitProb": 0.60,                 # Optional limit price
})
# Returns: list of bet objects (one per answer)
```

**Response details:**
- Returns array of bet objects, one per answer
- All bets share a `betGroupId` linking them together
- Some fills may have `amount: 0` (redemption during arbitrage)
- Amount is split evenly across answers

---

## Cancel Limit Order

```python
r = requests.post(f"{BASE}/bet/cancel/{bet_id}", headers=headers)
```

---

## Sell Shares

### Sell All Shares

```python
r = requests.post(f"{BASE}/market/{market_id}/sell", headers=headers, json={
    "outcome": "YES",  # Which shares to sell
})
```

### Sell Partial

```python
r = requests.post(f"{BASE}/market/{market_id}/sell", headers=headers, json={
    "outcome": "YES",
    "shares": 50,      # Number of shares to sell
})
```

### Sell MC Position

```python
r = requests.post(f"{BASE}/market/{market_id}/sell", headers=headers, json={
    "outcome": "YES",
    "answerId": answer_id,  # REQUIRED for MC
    "shares": 50,
})
```

### Auto-Redemption Note

When you hold both YES and NO shares in the same market, they automatically redeem against each other (1 YES + 1 NO = 1 mana). This means:
- Your net position may change after placing opposite bets
- Selling may fail with "no shares" if redemption already happened
- Check your actual position before selling

### Multi-Sell (Linked MC)

Sell positions across multiple answers:

```python
r = requests.post(f"{BASE}/multi-sell", headers=headers, json={
    "contractId": market_id,
    "answerIds": ["ans1", "ans2"],  # Sell all YES in these answers
})
# Returns: list of sell transactions
```

---

## Get Bets

### Filter Options

```python
r = requests.get(f"{BASE}/bets", params={
    "userId": "user123",             # Filter by user ID
    "username": "someuser",          # OR by username
    "contractId": "market123",       # Filter by market
    "contractSlug": "will-x-happen", # OR by market slug
    "limit": 1000,                   # Max 1000
    "before": "bet_id",              # Pagination: bets before this ID
    "after": "bet_id",               # Pagination: bets after this ID
    "beforeTime": 1700000000000,     # Filter by time (ms)
    "afterTime": 1699000000000,
    "kinds": "open-limit",           # Only open limit orders
    "order": "desc",                 # asc or desc
})
```

### Open Limit Orders

```python
# Get all open limit orders for a user
r = requests.get(f"{BASE}/bets", params={
    "userId": user_id,
    "kinds": "open-limit",
})

# Get open limit orders WITH market data (more useful)
r = requests.get(f"{BASE}/get-user-limit-orders-with-contracts", params={
    "userId": user_id,
})
# Returns: {"betsByContract": {...}, "contracts": [...]}
```

### Bet Object

```python
{
    "id": "bet123",
    "userId": "user123",
    "contractId": "market123",
    "answerId": "answer123",         # Only for MC markets

    "createdTime": 1700000000000,    # Milliseconds
    "amount": 100.0,                 # Mana spent
    "shares": 150.0,                 # Shares received
    "outcome": "YES",

    "probBefore": 0.5,
    "probAfter": 0.55,

    # Limit order fields
    "limitProb": 0.60,               # Only for limit orders
    "orderAmount": 100.0,            # Original order size
    "isFilled": False,
    "isCancelled": False,
    "fills": [...],                  # Partial fill history
    "expiresAt": 1700100000000,

    # Metadata
    "isApi": True,                   # Placed via API
    "isRedemption": False,           # Automatic share redemption
    "fees": {...},
}
```

---

## Probability History

There's no dedicated endpoint, but you can reconstruct it from bets:

```python
# Get all bets for a market, chronologically
r = requests.get(f"{BASE}/bets", params={
    "contractId": market_id,
    "order": "asc",
    "limit": 1000,
})

# Each bet has probBefore and probAfter
history = []
for bet in r.json():
    history.append({
        "time": bet["createdTime"],
        "prob": bet["probAfter"],
    })
```

---

## Bet Sizing Formulas

See [amm.md](amm.md) for:
- Computing shares from amount
- Computing amount needed for target shares
- How linked MC arbitrage works
