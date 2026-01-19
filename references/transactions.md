# Transactions (Txns)

Transactions track all mana/cash movements on the platform.

**Contents:** [Querying](#querying-transactions) · [Structure](#transaction-structure) · [Common Categories](#common-categories) · [All Categories](#all-category-groups)

---

## Querying Transactions

```python
import requests

BASE = "https://api.manifold.markets/v0"

# Get recent transactions
r = requests.get(f"{BASE}/txns", params={"limit": 100})

# Filter by user
r = requests.get(f"{BASE}/txns", params={"toId": "user123", "limit": 100})
r = requests.get(f"{BASE}/txns", params={"fromId": "user123", "limit": 100})

# Filter by category
r = requests.get(f"{BASE}/txns", params={"category": "UNIQUE_BETTOR_BONUS", "limit": 100})

# Filter by time (milliseconds)
r = requests.get(f"{BASE}/txns", params={"after": 1700000000000, "before": 1701000000000})

# Pagination with before cursor
txns = r.json()
last_id = txns[-1]["id"]
r = requests.get(f"{BASE}/txns", params={"before": last_id, "limit": 100})
```

---

## Transaction Structure

```python
{
    "id": "abc123",
    "createdTime": 1700000000000,
    "amount": 100.0,
    "token": "M$",              # "M$", "CASH", "SPICE", "SHARE"

    "fromId": "user123",        # or "BANK", "CONTRACT"
    "fromType": "USER",         # "USER", "BANK", "CONTRACT", "AD"
    "toId": "user456",
    "toType": "USER",

    "category": "MANA_PAYMENT",
    "description": "...",       # Optional
    "data": {...},              # Category-specific data
}
```

---

## Common Categories

| Category | From → To | Description | Data Fields |
|----------|-----------|-------------|-------------|
| `UNIQUE_BETTOR_BONUS` | BANK → USER | Creator bonus for new bettor | `contractId`, `uniqueNewBettorId`, `isPartner` |
| `BETTING_STREAK_BONUS` | BANK → USER | Daily betting streak reward | `contractId`, `currentBettingStreak` |
| `LOAN` | BANK → USER | Daily mana loan | `countsAsProfit` |
| `QUEST_REWARD` | BANK → USER | Quest completion reward | `questType`, `questCount` |
| `CONTRACT_RESOLUTION_PAYOUT` | CONTRACT → USER | Winnings from resolved market | `answerId`, `deposit`, `payoutStartTime` |
| `CREATE_CONTRACT_ANTE` | USER → CONTRACT | Initial market liquidity | - |
| `MANA_PAYMENT` | USER → USER | Direct mana transfer | `message`, `visibility`, `groupId` |
| `TIP` | USER → USER | Comment tip | `commentId`, `contractId` |
| `BOUNTY_AWARDED` | CONTRACT → USER | Bounty payout | - |
| `ADD_SUBSIDY` | USER → CONTRACT | Adding liquidity | - |
| `REFERRAL` | BANK → USER | Referral bonus | - |

---

## All Category Groups

### Bonuses (BANK → USER)
- `SIGNUP_BONUS` - New user bonus
- `REFERRAL` - Referral bonus
- `UNIQUE_BETTOR_BONUS` - Creator bonus for new bettor
- `BETTING_STREAK_BONUS` - Daily streak reward
- `QUEST_REWARD` - Quest completion
- `KYC_BONUS` - Identity verification bonus
- `PUSH_NOTIFICATION_BONUS` - Notification opt-in bonus

### Loans
- `LOAN` - Daily mana loan from BANK

### Transfers (USER → USER)
- `MANA_PAYMENT` - Direct transfer
- `TIP` - Comment tip
- `MANALINK` - Claimed manalink
- `CHARITY` - Donation to charity

### Trading
- `CONTRACT_RESOLUTION_PAYOUT` - Winnings from resolved market
- `CONTRACT_UNDO_RESOLUTION_PAYOUT` - Clawback on resolution undo

### Market Creation
- `CREATE_CONTRACT_ANTE` - Initial market liquidity
- `BOUNTY_POSTED` - Bounty question created
- `BOUNTY_AWARDED` - Bounty payout

### Liquidity
- `ADD_SUBSIDY` - Adding liquidity
- `REMOVE_SUBSIDY` - Removing liquidity

### Conversions
- `CONVERT_CASH` - Convert to cash
- `CONVERT_CASH_DONE` - Conversion complete
- `CONSUME_SPICE` - Consume spice tokens
- `CONSUME_SPICE_DONE` - Consumption complete
