# Supabase Direct Access

For bulk data fetching, Supabase is 10-100x faster than REST pagination.

---

## Basic Usage

```python
from bayesianbot.clients.manifold.client import ManifoldClient

mf = ManifoldClient()

# All markets (generator, efficient)
for market in mf.supabase.get_all_markets_sb(after_iso="2024-01-01"):
    print(market["question"])

# With filters
markets = mf.supabase.get_all_markets_sb(
    creator_id="user123",
    outcome_type="BINARY",
    order="desc",
)

# All users
for user in mf.supabase.get_all_users_sb():
    print(user["username"])

# League standings
leagues = mf.supabase.get_leagues_info_sb(season=10)
```

**Note**: Supabase bets endpoint is deprecated. Use REST API for bets.

---

## Available Methods

### Markets

```python
mf.supabase.get_all_markets_sb(
    after_iso="2024-01-01",      # Filter by creation date
    creator_id="user123",        # Filter by creator
    outcome_type="BINARY",       # BINARY, MULTIPLE_CHOICE, etc.
    order="desc",                # asc or desc by creation time
)
```

### User Positions

Faster than REST for bulk queries:

```python
positions = mf.supabase.get_user_positions_sb(
    user_id="user123",
    has_shares=True,             # Only positions with shares
    order_by="profit",
    limit=100,
)
# Returns: user_id, contract_id, answer_id, profit, total_shares_yes, total_shares_no, loan, data
```

### Portfolio History

Track portfolio value over time:

```python
history = mf.supabase.get_portfolio_history_sb(
    user_id="user123",
    after_ts="2024-01-01T00:00:00",
    limit=1000,
)
# Returns: ts, balance, investment_value, total_deposits, loan_total
```

### Follow Relationships

```python
following = mf.supabase.get_user_follows_sb(user_id="user123")   # Who user follows
followers = mf.supabase.get_user_follows_sb(follow_id="user123") # Who follows user
```

### Topic Groups

```python
groups = mf.supabase.get_groups_sb(order_by="importance_score", limit=100)
members = mf.supabase.get_group_members_sb(group_id="group123")
contracts = mf.supabase.get_group_contracts_sb(group_id="group123")
```

### Answers

Get answers with pool data for multi-choice markets:

```python
answers = mf.supabase.get_answers_sb(contract_id="market123")
# Returns: id, text, pool_yes, pool_no, prob, resolution, total_liquidity
```

### Other Methods

```python
# Liquidity provisions
liquidity = mf.supabase.get_contract_liquidity_sb(contract_id="market123")

# User reactions (likes)
reactions = mf.supabase.get_user_reactions_sb(user_id="user123")
```

---

## Available Tables

| Table | Description |
|-------|-------------|
| `contracts` | Markets |
| `users` | User profiles |
| `answers` | Multi-choice answers with pools |
| `user_contract_metrics` | User positions |
| `user_portfolio_history` | Portfolio value over time |
| `user_follows` | Follow relationships |
| `groups` | Topic groups |
| `group_members` | Group membership |
| `group_contracts` | Markets in groups |
| `contract_liquidity` | Liquidity provisions |
| `contract_comments` | Comments |
| `user_reactions` | Likes |
| `user_league_info` | League standings |
| `chart_annotations` | Market annotations |

**Not accessible**: `txns` (returns 500 error - use REST API instead)
