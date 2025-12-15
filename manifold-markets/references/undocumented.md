# Undocumented & Additional Endpoints

Endpoints not in the official docs but available via API. Some are at root path, some at `/v0/`.

---

## Path Convention

```python
import requests

base = "https://api.manifold.markets"
headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}

# Root path endpoints (no /v0/)
requests.get(f"{base}/request-loan", headers=headers)
requests.get(f"{base}/markets-by-ids", params=[("ids", "id1"), ("ids", "id2")])

# /v0/ endpoints
requests.post(f"{base}/v0/comment", json={...}, headers=headers)
requests.post(f"{base}/v0/managram", json={...}, headers=headers)
```

---

## Verified Root Path Endpoints

### Loans

```python
# GET /request-loan - Claim daily mana loan (auth required)
r = requests.get(f"{base}/request-loan", headers=headers)
# Returns: {"message": "Loan awarded"} or {"message": "Already awarded loan today"}

# GET /get-next-loan-amount - Check available loan amount
r = requests.get(f"{base}/get-next-loan-amount", params={"userId": "user123"})
# Returns: {"amount": 2409.01} or {"amount": 0}
```

### Batch Market Fetching

```python
# GET /markets-by-ids - Fetch multiple markets at once (max 100)
# Note: Use repeated 'ids' params, NOT comma-separated
r = requests.get(f"{base}/markets-by-ids",
    params=[("ids", "id1"), ("ids", "id2"), ("ids", "id3")])
# Returns: list of full market objects
```

### User Search

```python
# GET /search-users
r = requests.get(f"{base}/search-users", params={"term": "bayesian", "limit": 10})
# Returns: list of FullUser objects
```

### Extended Market Data

```python
# GET /get-contract - More fields than /v0/market/{id}
r = requests.get(f"{base}/get-contract", params={"contractId": "abc123"})
# Extra fields: description, elasticity, initialProbability, groupSlugs,
# importanceScore, freshnessScore, dailyScore, conversionScore, collectedFees
```

### Related Markets

```python
# GET /get-related-markets
r = requests.get(f"{base}/get-related-markets",
    params={"contractId": "abc123", "limit": 10})
# Returns: list of related Contract objects
```

### Notifications

```python
# GET /get-notifications (auth required)
r = requests.get(f"{base}/get-notifications", params={"limit": 50}, headers=headers)
# Returns: list of notification objects
```

### Feed

```python
# GET /get-feed - Personalized market feed
r = requests.get(f"{base}/get-feed",
    params={"userId": "user123", "limit": 20, "offset": 0})
# Returns: dict with feed data
```

### Reactions

```python
# POST /react - Like/unlike content (auth required)
r = requests.post(f"{base}/react", headers=headers, json={
    "contentId": "comment123",
    "contentType": "comment",  # "comment" | "contract"
    "reactionType": "like",    # "like"
    "remove": False            # True to unlike
})
```

### Private Messages

```python
# GET /get-channel-memberships - List DM channels (auth required)
r = requests.get(f"{base}/get-channel-memberships",
    params={"limit": 10}, headers=headers)
# Returns: {channels: [...], memberIdsByChannelId: {...}}

# GET /get-channel-messages - Read DM messages (auth required)
r = requests.get(f"{base}/get-channel-messages",
    params={"channelId": 59168, "limit": 20}, headers=headers)
# Returns: list of PrivateChatMessage objects
```

### Analytics

```python
# GET /get-mana-supply - Platform mana statistics
r = requests.get(f"{base}/get-mana-supply")
# Returns: mana supply stats

# GET /get-txn-summary-stats - Transaction statistics
r = requests.get(f"{base}/get-txn-summary-stats",
    params={"ignoreCategories": "LOAN,BETTING_STREAK_BONUS", "limitDays": 30})

# GET /get-daily-changed-metrics-and-contracts - Recent activity (auth required)
r = requests.get(f"{base}/get-daily-changed-metrics-and-contracts",
    params={"limit": 50}, headers=headers)
```

### Position Search

```python
# GET /search-contract-positions - Search positions by user name
r = requests.get(f"{base}/search-contract-positions",
    params={"term": "username", "contractId": "abc123", "limit": 20})
```

### Balance History

```python
# GET /get-balance-changes (auth required)
r = requests.get(f"{base}/get-balance-changes",
    params={"userId": "user123"}, headers=headers)
# Note: Does NOT support 'limit' param
```

---

## Verified /v0/ Endpoints

### Comments

```python
# POST /v0/comment - Post comment on market (auth required)
r = requests.post(f"{base}/v0/comment", headers=headers, json={
    "contractId": "abc123",
    "content": "Your comment text here",
    "replyToCommentId": "comment456"  # Optional, for replies
})
# Returns: the created comment object
```

### Mana Transfers

```python
# POST /v0/managram - Send mana to users (auth required)
r = requests.post(f"{base}/v0/managram", headers=headers, json={
    "amount": 100,
    "toIds": ["userId1", "userId2"],
    "message": "Thanks for the great market!",
    "groupId": "group123"  # Optional
})
```

### Follow Markets

```python
# POST /v0/follow-contract - Follow/unfollow market (auth required)
r = requests.post(f"{base}/v0/follow-contract", headers=headers, json={
    "contractId": "abc123",
    "follow": True  # False to unfollow
})
```

### Liquidity

```python
# POST /v0/market/{id}/add-liquidity - Add liquidity (auth required)
r = requests.post(f"{base}/v0/market/abc123/add-liquidity", headers=headers, json={
    "amount": 100
})
```

---

## Endpoint Reference Table

| Endpoint | Method | Path | Auth | Description |
|----------|--------|------|------|-------------|
| `request-loan` | GET | root | Yes | Claim daily mana loan |
| `get-next-loan-amount` | GET | root | No | Check available loan |
| `markets-by-ids` | GET | root | No | Batch fetch markets (repeated ids params) |
| `search-users` | GET | root | No | Search users by name |
| `get-contract` | GET | root | No | Extended market data |
| `get-related-markets` | GET | root | No | Similar markets |
| `get-notifications` | GET | root | Yes | User notifications |
| `get-feed` | GET | root | No | Personalized feed |
| `react` | POST | root | Yes | Like/unlike content |
| `get-channel-memberships` | GET | root | Yes | List DM channels |
| `get-channel-messages` | GET | root | Yes | Read DM messages |
| `get-mana-supply` | GET | root | No | Platform mana stats |
| `get-balance-changes` | GET | root | Yes | Balance history |
| `search-contract-positions` | GET | root | No | Search positions |
| `comment` | POST | /v0/ | Yes | Post comment |
| `managram` | POST | /v0/ | Yes | Send mana |
| `follow-contract` | POST | /v0/ | Yes | Follow/unfollow market |
| `market/{id}/add-liquidity` | POST | /v0/ | Yes | Add liquidity |

---

## Additional Endpoints (Not Yet Verified)

These exist in the schema but haven't been tested:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/get-user-limit-orders-with-contracts` | GET | Open limit orders with market data |
| `/unique-bet-group-count` | GET | Unique bettor count |
| `/get-site-activity` | GET | Site activity feed |
| `/create-public-chat-message` | POST | Post to public chat |
| `/set-channel-seen-time` | POST | Mark channel as read |
| `/unresolve` | POST | Unresolve market (creator only) |

See `bayesianbot/clients/manifold/undocumented.py` for implemented endpoints.

Full API schema: https://github.com/manifoldmarkets/manifold/blob/main/common/src/api/schema.ts
