# Supabase Direct Access

For bulk data fetching, Supabase is 10-100x faster than REST pagination.

**Key advantage:** Supabase can sort/filter by ANY field in the `data` JSON column (like `volume`, `prob`, `pool`), while REST endpoints have limited fixed sort options.

**Contents:** [Connection](#connection) · [Basic Queries](#basic-queries) · [Useful Queries](#useful-queries) · [Pagination](#pagination-for-large-datasets) · [Available Tables](#available-tables) · [JSON Columns](#accessing-json-columns) · [Notes](#notes)

---

## Connection

Manifold's Supabase is publicly readable with the anon key:

```python
from supabase import create_client

SUPABASE_URL = "https://pxidrgkatumlvfqaxcll.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB4aWRyZ2thdHVtbHZmcWF4Y2xsIiwicm9sZSI6ImFub24iLCJpYXQiOjE2Njg5OTUzOTgsImV4cCI6MTk4NDU3MTM5OH0.d_yYtASLzAoIIGdXUBIgRAGLBnNow7JG2SoaNMQ8ySg"

sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
```

---

## Basic Queries

```python
# Fetch markets
markets = sb.table("contracts").select("*").limit(100).execute()

# Filter by outcome type
binary = sb.table("contracts").select("*").eq("outcome_type", "BINARY").execute()

# Filter by creator
user_markets = sb.table("contracts").select("*").eq("creator_id", "user123").execute()

# Order and paginate
recent = sb.table("contracts").select("*").order("created_time", desc=True).range(0, 99).execute()
```

---

## Useful Queries

### All Open Markets

```python
import time

markets = (
    sb.table("contracts")
    .select("id, question, slug, close_time, mechanism, outcome_type, data")
    .is_("resolution", "null")
    .gt("close_time", int(time.time() * 1000))
    .execute()
)

# Probability is inside the 'data' JSON column
for m in markets.data:
    prob = m["data"].get("prob")  # For binary markets
```

### User Positions

```python
positions = (
    sb.table("user_contract_metrics")
    .select("contract_id, answer_id, total_shares_yes, total_shares_no, profit")
    .eq("user_id", "user123")
    .gt("total_shares_yes", 0)  # Has YES shares
    .execute()
)
```

### Multi-Choice Answers

```python
answers = (
    sb.table("answers")
    .select("id, text, pool_yes, pool_no, prob, resolution")
    .eq("contract_id", "market123")
    .execute()
)
```

### User Balance

```python
user = (
    sb.table("users")
    .select("id, username, balance, total_deposits")
    .eq("id", "user123")
    .single()
    .execute()
)
```

---

## Pagination for Large Datasets

Supabase limits responses to 1000 rows. For larger datasets, paginate:

```python
def fetch_all(table, select="*", **filters):
    """Fetch all rows from a table with pagination."""
    all_rows = []
    offset = 0
    batch_size = 1000

    while True:
        query = sb.table(table).select(select)
        for col, val in filters.items():
            query = query.eq(col, val)

        result = query.range(offset, offset + batch_size - 1).execute()
        rows = result.data
        all_rows.extend(rows)

        if len(rows) < batch_size:
            break
        offset += batch_size

    return all_rows

# Usage
all_markets = fetch_all("contracts", select="id, question, data")
```

---

## Available Tables

### contracts

| Column | Type | Notes |
|--------|------|-------|
| `id` | string | Market ID |
| `question` | string | Market title |
| `slug` | string | URL slug |
| `outcome_type` | string | BINARY, MULTIPLE_CHOICE, etc. |
| `mechanism` | string | cpmm-1, cpmm-multi-1, etc. |
| `resolution` | string | YES, NO, CANCEL, null |
| `close_time` | bigint | Milliseconds |
| `created_time` | bigint | Milliseconds |
| `creator_id` | string | User ID |
| `data` | jsonb | Full market data (prob, pool, answers, etc.) |
| `visibility` | string | public, unlisted |
| `importance_score` | float | Ranking score |

### answers

| Column | Type | Notes |
|--------|------|-------|
| `id` | string | Answer ID |
| `contract_id` | string | Market ID |
| `text` | string | Answer text |
| `pool_yes` | float | YES pool |
| `pool_no` | float | NO pool |
| `prob` | float | Current probability |
| `resolution` | string | YES, NO, null |
| `index` | int | Display order |
| `is_other` | boolean | Auto-added "Other" answer |

### user_contract_metrics

| Column | Type | Notes |
|--------|------|-------|
| `user_id` | string | User ID |
| `contract_id` | string | Market ID |
| `answer_id` | string | Answer ID (null for aggregate) |
| `total_shares_yes` | float | YES shares held |
| `total_shares_no` | float | NO shares held |
| `profit` | float | Current profit |
| `has_shares` | boolean | Has any position |
| `loan` | float | Outstanding loan |

### users

| Column | Type | Notes |
|--------|------|-------|
| `id` | string | User ID |
| `username` | string | Username |
| `name` | string | Display name |
| `balance` | float | Mana balance |
| `total_deposits` | float | Total deposited |
| `data` | jsonb | Extended user data |

### groups

| Column | Type | Notes |
|--------|------|-------|
| `id` | string | Group ID |
| `name` | string | Group name |
| `slug` | string | URL slug |
| `importance_score` | float | Ranking score |

### group_contracts

| Column | Type | Notes |
|--------|------|-------|
| `group_id` | string | Group ID |
| `contract_id` | string | Market ID |

---

## Accessing JSON Columns

The `data` column contains extended market/user info as JSON:

```python
# Get market with prob from data
result = sb.table("contracts").select("id, question, data").eq("id", "ABC123").single().execute()
market = result.data
prob = market["data"].get("prob")
pool = market["data"].get("pool")  # {"YES": 1000, "NO": 1000}
```

### Key fields in `data` JSON (contracts table)

| Field | Type | Notes |
|-------|------|-------|
| `volume` | float | All-time trading volume (mana) |
| `volume24Hours` | float | Last 24h volume |
| `prob` | float | Current probability (binary markets) |
| `pool` | object | `{"YES": n, "NO": n}` liquidity pools |
| `p` | float | AMM p-parameter (usually 0.5) |
| `creatorUsername` | string | For building URLs |
| `totalLiquidity` | float | Total liquidity in market |
| `uniqueBettorCount` | int | Number of unique traders |

### Sorting by JSON fields

Use arrow notation to sort by nested JSON fields:

```python
# Top markets by all-time volume
result = (
    sb.table("contracts")
    .select("id, question, slug, data")
    .eq("visibility", "public")
    .order("data->volume", desc=True)
    .limit(10)
    .execute()
)

# Top markets by unique traders
result = (
    sb.table("contracts")
    .select("id, question, data")
    .order("data->uniqueBettorCount", desc=True)
    .limit(10)
    .execute()
)
```

---

## Notes

- All timestamps are JavaScript milliseconds (not seconds)
- Supabase is **read-only** (no writes via anon key)
- Rate limits are generous but avoid hammering
- `bets` and `txns` tables are NOT accessible - use REST API
- For real-time updates, use WebSocket instead
