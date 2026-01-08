# Social API

Comments, reactions, follows, mana transfers, manalinks, and DMs.

**Contents:** [Comments](#comments) · [Reactions](#reactions) · [Mana Transfers](#mana-transfers-managrams) · [Manalinks](#manalinks) · [Follows](#follows) · [Direct Messages](#direct-messages) · [Transactions](#transactions) · [Feed](#feed) · [Site Activity](#site-activity) · [Headlines](#headlines) · [Posts](#posts) · [Transaction Stats](#transaction-stats)

---

## Comments

### Post Comment

```python
# Use 'markdown' for plain text or markdown formatting
r = requests.post(f"{BASE}/comment", headers=headers, json={
    "contractId": market_id,
    "markdown": "Your comment text here",
})

# Or with HTML
r = requests.post(f"{BASE}/comment", headers=headers, json={
    "contractId": market_id,
    "html": "<b>Bold</b> and <i>italic</i>",
})

# Note: 'content' field requires TipTap JSON format, not plain text

# Reply to existing comment
r = requests.post(f"{BASE}/comment", headers=headers, json={
    "contractId": market_id,
    "markdown": "Reply text",
    "replyToCommentId": "comment456",
})
```

### Get Comments

```python
r = requests.get(f"{BASE}/comments", params={
    "contractId": market_id,      # OR contractSlug
    "userId": user_id,            # Filter by commenter
    "limit": 1000,                # Max 5000
    "page": 0,
    "order": "newest",            # likes, newest, oldest
    "afterTime": 1700000000000,   # Only comments after this time
})
```

### Comment Threads

```python
# Get threaded comments (grouped by root)
r = requests.get(f"{BASE}/comment-threads", params={
    "contractId": market_id,
    "limit": 10,
    "page": 0,
})

# Get specific thread with all replies
r = requests.get(f"{BASE}/comment-thread", params={
    "contractId": market_id,
    "commentId": root_comment_id,
})
```

### Hide/Delete Comment

```python
r = requests.post(f"{BASE}/hide-comment", headers=headers, json={
    "commentPath": "comments/abc123",  # Full path
    "action": "hide",                  # hide or delete
})
```

### Pin Comment (Market Creator)

```python
r = requests.post(f"{BASE}/pin-comment", headers=headers, json={
    "commentId": "comment123",
})
```

### Best Comments

```python
r = requests.get(f"{BASE}/get-best-comments", params={
    "contractId": market_id,
    "limit": 10,
})
```

### Comment Reactions

```python
r = requests.get(f"{BASE}/comment-reactions", params={
    "commentId": "comment123",
})
```

### Comment Content Format

Comments use TipTap/ProseMirror JSON format:

```python
{
    "type": "doc",
    "content": [
        {"type": "paragraph", "content": [
            {"type": "text", "text": "Hello "},
            {"type": "mention", "attrs": {"label": "username", "id": "user123"}}
        ]}
    ]
}
```

Extract plain text:

```python
def extract_text(content):
    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "text":
                return node.get("text", "")
            if node.get("type") == "mention":
                return f"@{node.get('attrs', {}).get('label', '')}"
            if "content" in node:
                return " ".join(walk(c) for c in node["content"])
        return ""
    return walk(content)
```

---

## Reactions

```python
# Root path
r = requests.post("https://api.manifold.markets/react", headers=headers, json={
    "contentId": "comment123",
    "contentType": "comment",    # comment, contract
    "reactionType": "like",
    "remove": False,             # True to unlike
})
```

---

## Mana Transfers (Managrams)

### Send Mana

```python
r = requests.post(f"{BASE}/managram", headers=headers, json={
    "amount": 100,
    "toIds": ["userId1", "userId2"],   # Can send to multiple
    "message": "Thanks!",               # Optional
})
```

### Get Managrams

```python
r = requests.get(f"{BASE}/managrams", params={
    "toId": user_id,           # Received by
    "fromId": user_id,         # Sent by
    "limit": 100,
    "before": 1700000000000,   # Before this time
    "after": 1699000000000,
})
```

### Donate

```python
r = requests.post(f"{BASE}/donate", headers=headers, json={
    "amount": 100,
    "to": user_id,
})
```

---

## Manalinks

**⚠️ Admin only** - Manalink creation requires admin privileges.

```python
r = requests.post(f"{BASE}/manalink", headers=headers, json={
    "amount": 100,
    "expiresTime": 1735689600,   # Unix timestamp (optional)
    "maxUses": 10,               # Max claims (optional)
    "message": "Free mana!",     # Optional
})
# Returns: {"slug": "abc123xyz"}
# Full URL: https://manifold.markets/link/abc123xyz
```

---

## Follows

### Follow/Unfollow Market

```python
r = requests.post(f"{BASE}/follow-contract", headers=headers, json={
    "contractId": market_id,
    "follow": True,    # False to unfollow
})
```

### Followed Groups

```python
r = requests.get(f"{BASE}/get-followed-groups", params={"userId": user_id})
```

---

## Direct Messages

### List DM Channels

```python
# Root path, requires auth
r = requests.get("https://api.manifold.markets/get-channel-memberships",
    params={"limit": 10}, headers=headers)
# Returns: {"channels": [...], "memberIdsByChannelId": {...}}
```

### Read DM Messages

```python
# Root path, requires auth
r = requests.get("https://api.manifold.markets/get-channel-messages",
    params={"channelId": 59168, "limit": 20}, headers=headers)
# Returns: list of PrivateChatMessage objects
```

### Send DM Message

```python
# Root path, requires auth
# Note: channelId must be a STRING, not number
r = requests.post("https://api.manifold.markets/create-public-chat-message",
    headers=headers, json={
        "channelId": "59168",  # String, not int!
        "content": {
            "type": "doc",
            "content": [{"type": "paragraph", "content": [
                {"type": "text", "text": "Your message here"}
            ]}]
        }
    })
# Returns: {"id": 123, "channelId": "59168", "userId": "...", ...}
```

**Note:** You can only send to existing channels. There's no API endpoint to create new DM channels - that must be done through the UI.

### Mark Channel as Read

```python
# Root path, requires auth
r = requests.post("https://api.manifold.markets/set-channel-seen-time",
    headers=headers, json={"channelId": 59168})
```

---

## Transactions

Track all mana movements (bets, bonuses, transfers, payouts).

### Get Transactions

```python
r = requests.get(f"{BASE}/txns", params={
    "toId": user_id,           # Received by
    "fromId": user_id,         # Sent by
    "category": "UNIQUE_BETTOR_BONUS",  # Filter by type
    "limit": 100,
    "before": 1700000000000,
    "after": 1699000000000,
})
```

### Transaction Object

```python
{
    "id": "abc123",
    "createdTime": 1700000000000,
    "amount": 100.0,
    "token": "M$",               # M$ (mana)

    "fromId": "user123",         # or "BANK", "CONTRACT"
    "fromType": "USER",          # USER, BANK, CONTRACT, AD
    "toId": "user456",
    "toType": "USER",

    "category": "MANA_PAYMENT",
    "description": "...",
    "data": {...},               # Category-specific
}
```

### Common Categories

| Category | From → To | Description |
|----------|-----------|-------------|
| `UNIQUE_BETTOR_BONUS` | BANK → USER | Creator bonus for new bettor |
| `BETTING_STREAK_BONUS` | BANK → USER | Daily streak reward |
| `LOAN` | BANK → USER | Daily mana loan |
| `QUEST_REWARD` | BANK → USER | Quest completion |
| `CONTRACT_RESOLUTION_PAYOUT` | CONTRACT → USER | Market winnings |
| `CONTRACT_UNDO_RESOLUTION_PAYOUT` | USER → CONTRACT | Unresolve reversal |
| `CREATE_CONTRACT_ANTE` | USER → CONTRACT | Initial liquidity |
| `MANA_PAYMENT` | USER → USER | Direct transfer |
| `TIP` | USER → USER | Comment tip |
| `BOUNTY_AWARDED` | CONTRACT → USER | Bounty payout |
| `ADD_SUBSIDY` | USER → CONTRACT | Adding liquidity |
| `REFERRAL` | BANK → USER | Referral bonus |

See [transactions.md](transactions.md) for full category list.

### Balance Changes

More detailed view of balance changes including answer context:

```python
# Root path
r = requests.get("https://api.manifold.markets/get-balance-changes", params={
    "userId": user_id,
    "after": 1700000000000,  # Milliseconds
    "limit": 100,
})
# Returns: [{amount, answer: {text, id}, contractId, createdTime}, ...]
```

---

## Feed

```python
# Root path
r = requests.get("https://api.manifold.markets/get-feed",
    params={"userId": user_id, "limit": 20, "offset": 0})
```

---

## Site Activity

```python
# Global activity feed (all users)
r = requests.get(f"{BASE}/get-site-activity", params={"limit": 50})
```

---

## Headlines

```python
# General headlines
r = requests.get(f"{BASE}/headlines")

# Politics headlines
r = requests.get(f"{BASE}/politics-headlines")
```

---

## Posts

Manifold has a blog-like posts system separate from market comments.

```python
# Get posts
r = requests.get(f"{BASE}/get-posts", params={"limit": 20})

# Create post
r = requests.post(f"{BASE}/create-post", headers=headers, json={
    "title": "Post title",
    "content": "Post content...",
})

# Update post
r = requests.post(f"{BASE}/update-post", headers=headers, json={
    "postId": "post123",
    "title": "Updated title",
})

# Follow/unfollow post
r = requests.post(f"{BASE}/follow-post", headers=headers, json={
    "postId": "post123",
    "follow": True,
})

# Comment on post
r = requests.post(f"{BASE}/create-post-comment", headers=headers, json={
    "postId": "post123",
    "content": "Comment text",
})
```

---

## Transaction Stats

```python
# Transaction summary statistics
r = requests.get(f"{BASE}/get-txn-summary-stats", params={
    "ignoreCategories": "LOAN,BETTING_STREAK_BONUS",
    "limitDays": 30,
})

# Mana summary statistics
r = requests.get(f"{BASE}/get-mana-summary-stats")
```
