# Markets API

Everything about creating, fetching, searching, editing, and resolving markets.

**Contents:** [Fetch Markets](#fetch-markets) · [Create Market](#create-market) · [Edit Market](#edit-market) · [Resolve Market](#resolve-market) · [Liquidity](#liquidity) · [Groups/Topics](#groups--topics) · [Bounty Markets](#bounty-markets) · [Moderation](#moderation)

---

## Fetch Markets

### By ID or Slug

```python
# By ID (full market object with answers, description, etc.)
r = requests.get(f"{BASE}/market/{market_id}")

# By ID - lightweight (fewer fields, faster)
r = requests.get(f"{BASE}/market/{market_id}/lite")

# By slug (URL-friendly name)
r = requests.get(f"{BASE}/slug/{slug}")

# Extended data (more fields: elasticity, scores, collectedFees)
# Note: Root path, not /v0/
r = requests.get("https://api.manifold.markets/get-contract",
    params={"contractId": market_id})
```

### Batch Fetch

```python
# Batch fetch by IDs (max 100) - ROOT PATH
# Note: Use 'ids[]' bracket notation for array params
r = requests.get("https://api.manifold.markets/markets-by-ids",
    params=[("ids[]", id1), ("ids[]", id2), ("ids[]", id3)])
# Returns extended market objects (40+ fields including scoring/analytics)

# Batch probability fetch (up to 100)
r = requests.get(f"{BASE}/market-probs",
    params=[("ids[]", mid) for mid in market_ids])
```

### List Markets

```python
r = requests.get(f"{BASE}/markets", params={
    "limit": 1000,                    # Max 1000
    "sort": "created-time",           # See sort options below
    "order": "desc",                  # asc, desc
    "before": "market_id_cursor",     # Pagination cursor
    "userId": "creator_id",           # Filter by creator
    "groupId": "group_id",            # Filter by group/topic
})

# /markets sort options (from schema.ts):
# created-time, updated-time, last-bet-time, last-comment-time
```

### Search Markets

```python
r = requests.get(f"{BASE}/search-markets", params={
    "term": "AI",
    "sort": "score",        # See sort options below
    "filter": "open",       # all, open, closed, resolved, closing-this-month, closing-next-month
    "contractType": "BINARY",  # BINARY, MULTIPLE_CHOICE, PSEUDO_NUMERIC, POLL, etc.
    "topicSlug": "ai",      # Filter by topic/group slug
    "creatorId": "user_id",
    "limit": 100,           # Max 100
    "offset": 0,
})

# /search-markets sort options (from schema.ts):
# score (default), newest, daily-score, freshness-score, 24-hour-vol,
# most-popular, liquidity, subsidy, last-updated, close-date,
# start-time, resolve-date, random, bounty-amount, prob-descending, prob-ascending
#
# WARNING: There is NO "volume" sort option. For all-time volume ranking, use Supabase.
```

**Note:** Search returns fewer fields than full fetch. Missing: `answers`, `description`, `shouldAnswersSumToOne`. Always fetch full market if you need MC answer data.

### Search Markets (Full Objects)

```python
# Returns full market objects instead of lite
# Root path, not /v0/
r = requests.get("https://api.manifold.markets/search-markets-full", params={
    "term": "AI",
    "filter": "open",
    "limit": 50,
})
```

### Answers (Multiple Choice)

```python
# Get all answers for a market
r = requests.get(f"{BASE}/market/{market_id}/answers")

# Get single answer by ID
r = requests.get(f"{BASE}/answer/{answer_id}")
```

### Related Markets

```python
# Root path
r = requests.get("https://api.manifold.markets/get-related-markets",
    params={"contractId": market_id, "limit": 10})
# Returns: {"marketsFromEmbeddings": [...]} - NOT a bare list
markets = r.json()["marketsFromEmbeddings"]
```

---

## Create Market

```python
r = requests.post(f"{BASE}/market", headers=headers, json={
    # Required
    "question": "Will X happen by 2025?",
    "outcomeType": "BINARY",          # See Market Types below
    "liquidityTier": 100,             # Initial liquidity (min 100, required)

    # Optional (all types) - see Description Formats section below
    "description": "Resolution criteria...",  # Plain text OR TipTap JSON
    "descriptionMarkdown": "**Bold** criteria",  # Markdown (images stripped!)
    "descriptionHtml": "<b>Bold</b>",  # HTML (images work with <img>)
    "closeTime": 1735689600000,        # Milliseconds (omit for perpetual)
    "visibility": "public",            # public, unlisted
    "groupIds": ["group1", "group2"],  # Max 5 groups/topics — must be real UUIDs, NOT slugs
    # To get an ID from a slug: GET /v0/group/{slug} → use the "id" field

    # Binary-specific
    "initialProb": 50,                 # 1-99

    # Multiple choice-specific
    "answers": ["Option A", "Option B", "Option C"],
    "addAnswersMode": "ANYONE",        # DISABLED, ONLY_CREATOR, ANYONE
    "shouldAnswersSumToOne": True,     # True for linked MC, False for independent

    # Numeric-specific (PSEUDO_NUMERIC)
    "min": 0,
    "max": 100,
    "initialValue": 50,
    "isLogScale": False,

    # Bounty-specific
    "totalBounty": 500,                # Min 50
})
```

**Notes:**
- `liquidityTier` is required (minimum 100 mana)
- `shouldAnswersSumToOne` is a **boolean**, not a string
- For linked MC (`shouldAnswersSumToOne: true`), an "Other" answer is auto-added when `addAnswersMode` is `"ANYONE"` or `"ONLY_CREATOR"`. Independent MC markets don't get "Other".

#### `addAnswersMode`: fixed-at-creation consequences

For linked MC (`shouldAnswersSumToOne: true`), `addAnswersMode` has consequences that are baked in at creation and cannot be undone later:

- **`DISABLED` creates no `Other`.** A linked MC market created with `addAnswersMode: "DISABLED"` has no auto-generated `Other` answer — the final bucket is whatever text the creator typed. This is a one-way door: you cannot add answers later.
- **Flipping `addAnswersMode` later does not retroactively create `Other`.** If a linked MC market was created with `DISABLED` and is later updated to `ANYONE` / `ONLY_CREATOR`, no `Other` answer is added. The presence/absence of `Other` is fixed by the *initial* `addAnswersMode`.
- **`addAnswersMode` is not editable on linked MC, and the API silently drops the change.** `POST /v0/market/:id/update` with `addAnswersMode` on a `shouldAnswersSumToOne: true` market returns **HTTP 200**, but on re-fetch the field is unchanged. Independent MC (`shouldAnswersSumToOne: false`) accepts the change normally. Pick the right value at creation on linked MC, and always re-fetch to verify writes.

### Description Formats

| Parameter | Format | Images? |
|-----------|--------|---------|
| `description` | Plain text OR TipTap JSON | ✅ Yes (with TipTap) |
| `descriptionMarkdown` | Markdown string | ❌ Stripped |
| `descriptionHtml` | HTML string | ✅ Yes (with `<img>`) |

**To include images, use HTML or TipTap JSON:**

```python
description = {
    "type": "doc",
    "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "Here's a chart:"}]},
        {"type": "image", "attrs": {"src": "https://example.com/image.png", "alt": "Chart"}},
        {"type": "paragraph", "content": [{"type": "text", "text": "Analysis continues..."}]},
    ]
}

r = requests.post(f"{BASE}/market", headers=headers, json={
    "question": "Will X happen?",
    "outcomeType": "BINARY",
    "liquidityTier": 100,
    "initialProb": 50,
    "description": description,  # TipTap JSON object, NOT descriptionMarkdown
})
```

**Common TipTap node types:**

| Node | Description | Attrs |
|------|-------------|-------|
| `paragraph` | Text container | - |
| `text` | Inline text | - |
| `image` | Image | `src`, `alt` |
| `heading` | Heading | `level` (1-6) |
| `bulletList` | Unordered list | - |
| `orderedList` | Ordered list | - |
| `listItem` | List item | - |
| `codeBlock` | Code block | `language` |
| `blockquote` | Quote | - |
| `hardBreak` | Line break | - |

### Market Types

| outcomeType | Use Case | Key Params |
|-------------|----------|------------|
| `BINARY` | YES/NO questions | `initialProb` |
| `MULTIPLE_CHOICE` | Multiple options | `answers`, `addAnswersMode`, `shouldAnswersSumToOne` |
| `PSEUDO_NUMERIC` | Numeric range | `min`, `max`, `initialValue`, `isLogScale` |
| `POLL` | Non-tradeable voting | `answers` |
| `BOUNTIED_QUESTION` | Bounty for best answer | `totalBounty` |

---

## Edit Market

### Immutable After Creation

Some fields cannot be changed via the API once a market exists. If you need any of these to differ, create a new market and resolve/cancel the old one — there is no update endpoint that accepts them.

| Field | Note |
|-------|------|
| `outcomeType` | Structural (BINARY, MULTIPLE_CHOICE, …) |
| `mechanism` | Structural (cpmm-1, cpmm-multi-1, none) |
| `shouldAnswersSumToOne` | Structural — fixes linked vs independent MC |
| `slug` | Frozen at creation; renaming `question` does **not** regenerate it |
| `creatorId`, `createdTime`, `token` | Identity/ownership fields |
| `initialProb` (BINARY) | Only the *current* `p` and pool are mutable, via trades/liquidity ops |
| `min`, `max`, `isLogScale` (PSEUDO_NUMERIC) | Structural numeric range |

Note: `addAnswersMode` on linked MC (`shouldAnswersSumToOne=true`) is effectively fixed at creation as well — see the create-market section.

### Verifying Writes

Some write endpoints return `{"success": true}` (or 200 OK) even when the requested change did **not** persist. Treat the response as a hint, not proof — always re-fetch and inspect the field you edited.

```python
# Pattern: write, re-fetch, check, retry-with-backoff if read is stale
import time

def verify(market_id, field, expected, attempts=3):
    for i in range(attempts):
        m = requests.get(f"{BASE}/market/{market_id}").json()
        if m.get(field) == expected or expected in (m.get(field) or []):
            return True
        time.sleep(2 ** i)  # 1s, 2s, 4s — covers typical 5-15s read-after-write cache lag
    return False
```

**Read-after-write cache lag:** A `GET /v0/market/:id` issued immediately after a mutation can return stale data for ~5–15s before the write shows up. If your first re-fetch shows old state, wait and retry once or twice before declaring failure.

**Known silent-failure cases:**

| Endpoint | What looks fine | What actually happened |
|----------|-----------------|------------------------|
| `POST /v0/market/:id/update` with `addAnswersMode` | HTTP 200 | On linked MC (`shouldAnswersSumToOne: true`) the field is silently unchanged. Independent MC accepts the change normally. |
| `POST /edit-answer-cpmm` | `{"status": "success"}` | Re-check `answers[].text` — the short success body doesn't guarantee persistence. |

For comparison, *non*-silent failures with similar shapes — these throw, so a try/except is enough:
- `POST /v0/market/:id/group` past the 5-group cap returns **HTTP 403** with `"A question can only have up to 5 topic tags."` (not silent — your `r.raise_for_status()` will catch it).

If you discover another silent-failure endpoint, please open an issue.

### Update Properties

```python
r = requests.post(f"{BASE}/market/{market_id}/update", headers=headers, json={
    "question": "Updated question?",           # Optional
    "closeTime": 1735689600000,                # Optional
    "visibility": "unlisted",                  # Optional: unlisted, public
    "addAnswersMode": "ANYONE",                # Optional: ONLY_CREATOR, ANYONE
    "coverImageUrl": "https://...",            # Optional, or null to remove

    # Description fields (same options as create, but different types):
    "description": "Plain text only",          # z.string() — does NOT accept TipTap objects
    "descriptionJson": '{"type":"doc",...}',   # TipTap JSON stringified — USE THIS for rich text
    "descriptionHtml": "<p>Bold</p>",          # HTML string
    "descriptionMarkdown": "**Bold**",         # Markdown string (images stripped)
})
```

**Important:** Unlike the create endpoint where `description` accepts a TipTap object directly,
the update endpoint's `description` field is `z.string()` only and will reject objects with a 400.
To update with rich TipTap content (e.g. `contract-mention` nodes), use `descriptionJson` with
`json.dumps(tiptap_object)` — this works and preserves all node types including custom ones.

### Close Market

```python
# Close immediately
r = requests.post(f"{BASE}/market/{market_id}/close", headers=headers)

# Close at specific time
r = requests.post(f"{BASE}/market/{market_id}/close", headers=headers, json={
    "closeTime": 1735689600000  # Milliseconds
})
```

### Add Answer (Multiple Choice)

```python
r = requests.post(f"{BASE}/market/{market_id}/answer", headers=headers, json={
    "text": "New option"  # 1-255 chars
})
# Returns: {"newAnswerId": "abc123"}
```

**Note:** Adding answers costs mana as liquidity subsidy (`ADD_SUBSIDY` transaction). Cost scales with market liquidity:

### Edit Answer (Multiple Choice)

Rename an existing answer or change its color. **Root path, not `/v0/`** — and not surfaced by Manifold's public API docs.

```python
# Edit answer text (and optionally color) on a cpmm-multi-1 market
r = requests.post("https://api.manifold.markets/edit-answer-cpmm", headers=headers, json={
    "contractId": market_id,
    "answerId": answer_id,
    "text": "Renamed answer",     # required
    # "color": "#ff0099",         # optional; if provided, must be a string (null returns 400)
})
# Returns: {"status": "success"}
```

**Notes:**
- Creator only.
- Verified on linked MC (`shouldAnswersSumToOne=true`); the endpoint name implies cpmm-multi-1 scope and it has not been confirmed to work elsewhere.
- Always re-fetch and check `answers[].text` — `{"status": "success"}` is not proof the write persisted.

| Tier | Cost | Triggered when liquidity/answer is... |
|------|------|---------------------------------------|
| 0 | 25 | Low |
| 1 | 100 | Medium |
| 2 | 1000 | High |
| 3 | 10000 | Very high |

---

## Resolve Market

### Binary Markets

```python
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "YES",  # YES, NO, MKT, CANCEL
})

# Partial resolution (MKT)
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "MKT",
    "probabilityInt": 75,  # 0-100, payout ratio
})
```

### Multiple Choice - Single Winner

```python
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "CHOOSE_ONE",
    "answerId": "winning_answer_id",
})
```

### Multiple Choice - Split Resolution

```python
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "CHOOSE_MULTIPLE",
    "resolutions": [
        {"answerId": "ans1", "pct": 60},
        {"answerId": "ans2", "pct": 40},
    ]  # Must sum to 100
})
```

### Multiple Choice - Independent (per-answer)

For markets created with `shouldAnswersSumToOne: false`, each answer behaves like its own binary market and can be resolved independently with `outcome: "YES"` or `"NO"` plus the `answerId`:

```python
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "NO",          # or "YES"
    "answerId": answer_id,
})
# 200 OK -> {"message": "success"}
```

After this call:
- The targeted answer flips to `resolution: "NO"` (or `"YES"`) and stops trading.
- The market itself remains `isResolved: false`.
- Other answers stay open and tradable.
- Subsequent calls with different `answerId`s incrementally resolve the rest.

This is the typical pattern for walking a "Before {month} {year}" release-date ladder — each month resolves NO as it lapses, eventually one resolves YES.

**Not valid on linked MC** (`shouldAnswersSumToOne: true`): use `CHOOSE_ONE` / `CHOOSE_MULTIPLE` / `MKT` instead, since exactly one answer can resolve YES.

### Cancel

```python
r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
    "outcome": "CANCEL",
})
```

### Unresolve

Reverts a resolution, returning payouts to the pool. Creates `CONTRACT_UNDO_RESOLUTION_PAYOUT` transactions.

```python
# Root path, not /v0/
r = requests.post("https://api.manifold.markets/unresolve", headers=headers, json={
    "contractId": market_id,
})
# Returns: {"success": true}
```

**Notes:**
- Creator only
- Creates reversal transactions for all payouts
- Market returns to unresolved state

### Retry Semantics: Transient HTTP 500 on /resolve

`POST /v0/market/:id/resolve` can return **HTTP 500** with a Postgres `code: "40001"` error and the message `could not serialize access due to read/write dependencies among transactions`. This is a transient SERIALIZABLE-isolation conflict on the backend (concurrent payout/txn updates), not a malformed request — but the response wrapper makes it look like a permanent server error.

**Critical caveat: the backend may have already committed.** When the conflict is detected late in the transaction, the resolution can be partially or fully applied before the 500 is raised. Verified empirically: a 500 came back, yet on re-fetch the answer was already `resolution: "NO"` and payouts had been issued.

So: **don't blindly retry on 500** — you can double-resolve, or get a confusing second-attempt error. Always re-fetch state between attempts and skip if the desired resolution is already in place.

```python
import time

def resolve_with_retry(market_id, answer_id, outcome, max_attempts=4):
    for attempt in range(max_attempts):
        # Pre-check: if the previous attempt actually committed, short-circuit.
        m = requests.get(f"{BASE}/market/{market_id}").json()
        for a in m.get("answers", []):
            if a["id"] == answer_id and a.get("resolution") == outcome:
                return "already-resolved"

        try:
            r = requests.post(f"{BASE}/market/{market_id}/resolve", headers=headers, json={
                "outcome": outcome, "answerId": answer_id,
            })
            r.raise_for_status()
            return "success"
        except requests.HTTPError as e:
            if e.response.status_code in (500, 503) and attempt < max_attempts - 1:
                time.sleep(2 + 2 * attempt)  # 2s, 4s, 6s backoff
                continue
            raise
```

The pre-check is what makes this safe: a prior 500 that actually committed is detected as `already-resolved` on the next iteration.

---

## Liquidity

```python
# Add liquidity
r = requests.post(f"{BASE}/market/{market_id}/add-liquidity", headers=headers, json={
    "amount": 100
})

# Remove liquidity (creator only)
r = requests.post(f"{BASE}/market/{market_id}/remove-liquidity", headers=headers, json={
    "amount": 50
})
```

---

## Groups / Topics

Markets can belong to up to 5 groups (also called "topics").

```python
# List all groups
r = requests.get(f"{BASE}/groups")

# Get group by slug or ID
r = requests.get(f"{BASE}/group/{slug}")
r = requests.get(f"{BASE}/group/by-id/{group_id}")

# Search groups (root path, not /v0/)
r = requests.get("https://api.manifold.markets/search-groups", params={"term": "politics", "limit": 10})
# Returns: {"full": [...], "lite": [...]} - use "full" for complete group objects

# Search your followed groups (root path, requires auth)
r = requests.get("https://api.manifold.markets/search-my-groups", params={"term": "tech"}, headers=headers)

# Get markets in a group
r = requests.get(f"{BASE}/group/by-id/{group_id}/markets")

# Get groups with most popular markets (root path, requires auth)
r = requests.get("https://api.manifold.markets/get-groups-with-top-contracts", headers=headers)

# Get groups a market belongs to
r = requests.get(f"{BASE}/market/{market_id}/groups")

# Add market to group
r = requests.post(f"{BASE}/market/{market_id}/group", headers=headers, json={
    "groupId": "group_id"
})

# Remove market from group
r = requests.post(f"{BASE}/market/{market_id}/group", headers=headers, json={
    "groupId": "group_id",
    "remove": True
})
```

### Group Object

```python
{
    "id": "abc123",
    "slug": "technology",
    "name": "Technology",
    "about": "Tech markets",
    "creatorId": "user123",
    "totalMembers": 1500,
    "privacyStatus": "public",  # public, curated
    "importanceScore": 0.85,
}
```

---

## Bounty Markets

```python
# Add bounty to existing bounty market
r = requests.post(f"{BASE}/market/{market_id}/add-bounty", headers=headers, json={
    "amount": 100
})

# Award bounty to a comment
r = requests.post(f"{BASE}/market/{market_id}/award-bounty", headers=headers, json={
    "amount": 50,
    "commentId": "comment_id"
})
```

---

## Moderation

```python
# Block market (creator/mod only)
r = requests.post(f"{BASE}/market/{market_id}/block", headers=headers)

# Unblock market
r = requests.post(f"{BASE}/market/{market_id}/unblock", headers=headers)
```
