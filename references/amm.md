# AMM Simulation

Complete guide for simulating Manifold's AMM (Constant Product Market Maker) locally.

**Contents:** [Probability Formula](#probability-formula) · [Shares from Amount](#computing-shares-from-amount) · [Amount from Shares](#computing-amount-from-shares-p05-only) · [Linked MC Arbitrage](#linked-mc-arbitrage-shouldanswerssumtoonetrue) · [Auto-Redemption](#auto-redemption-binary-markets) · [Validating](#validating-simulations) · [Source Files](#source-files)

---

## Probability Formula

```python
# General formula with weighting parameter p
prob = pool_no**(1-p) / (pool_yes**p + pool_no**(1-p))

# For p=0.5 (ALL multi-choice markets), simplifies to:
prob = pool_no / (pool_yes + pool_no)
```

**Critical:** Multi-choice markets ALWAYS use `p=0.5`. Only binary markets have variable `p`.

---

## Computing Shares from Amount

When you spend `amount` buying YES:
```python
k = pool_yes**p * pool_no**(1-p)  # Invariant (preserved)
new_pool_no = pool_no + amount
new_pool_yes = (k / new_pool_no**(1-p))**(1/p)
shares = pool_yes - new_pool_yes
```

---

## Computing Amount from Shares (p=0.5 only)

Closed-form solution from Manifold's `calculateAmountToBuySharesFixedP`:
```python
# For YES shares:
amount = (shares - y - n + sqrt(4*n*shares + (y+n-shares)**2)) / 2

# For NO shares:
amount = (shares - y - n + sqrt(4*y*shares + (y+n-shares)**2)) / 2
```

Source: [Wolfram Alpha derivation](https://www.wolframalpha.com/input?i=%28y%2Bb-s%29%5E0.5+*+%28n%2Bb%29%5E0.5+%3D+y+%5E+0.5+*+n+%5E+0.5%2C+solve+b)

---

## Linked MC Arbitrage (shouldAnswersSumToOne=true)

Buying YES on one answer requires rebalancing ALL answers to maintain sum(probs)=1.

### Algorithm (from `calculate-cpmm-arbitrage.ts`)

1. Binary search for `noShares` to buy in ALL answers (including target)
2. Redemption returns: `noShares * (numAnswers - 1)` mana
3. Extra mana buys YES on target answer
4. Target: find `noShares` where sum(probs) = 1 after all trades

```python
# Pseudocode
def arbitrage_bet_yes(all_pools, target_id, bet_amount):
    # Binary search for noShares
    noShares = binary_search(lambda ns: prob_sum_after(ns) - 1.0)

    # Buy NO in every answer
    total_no_cost = 0
    for answer in all_pools:
        cost = amount_for_shares(answer.pool, noShares, "NO")
        apply_trade(answer, cost, "NO")
        total_no_cost += cost

    # Redemption: n answers with noShares NO each = noShares*(n-1) mana back
    extra_mana = noShares * (len(all_pools) - 1) - total_no_cost

    # Buy YES on target with extra mana
    apply_trade(target, extra_mana, "YES")
```

### Why Redemption Works

When you hold 1 YES + 1 NO of the same answer, you can redeem for $1. The NO purchases across all answers create redemption opportunities:
- You have `noShares` NO in each of `n` answers
- When market resolves, one answer wins (those NO worth $0), `n-1` lose (those NO worth $1 each)
- Expected redemption value: `noShares * (n-1)`

---

## Auto-Redemption (Binary Markets)

When you hold both YES and NO shares in a binary market, they automatically redeem:

```
1 YES share + 1 NO share = 1 mana (returned to balance)
```

**Practical implications:**
- If you bet YES then bet NO, your YES shares may be partially/fully redeemed
- Your actual position after multiple trades may differ from what you expect
- When selling, check your actual position first - you may have fewer shares than you think
- The `isRedemption` field in bet responses indicates redemption occurred

**Example:** You buy 20 YES shares, then buy 30 NO shares. You now have 0 YES and 10 NO (not 20 YES and 30 NO), plus mana from the 20 redeemed pairs.

---

## Validating Simulations

Use `dryRun` to validate your AMM math against the API:
```python
import requests

r = requests.post("https://api.manifold.markets/v0/bet",
    headers={"Authorization": f"Key {API_KEY}"},
    json={"contractId": market_id, "amount": 100, "outcome": "YES", "dryRun": "true"}
)
api_prob = r.json()["probAfter"]
our_prob = simulate_bet(pool_state, 100, "YES")
assert abs(api_prob - our_prob) < 0.001
```

**Note:** `dryRun` response includes `fills` with `matchedBetId` when limit orders get matched. Pure AMM simulation won't account for limit order fills - expect small discrepancies when limit orders exist.

---

## Source Files

- **Binary CPMM**: [calculate-cpmm.ts](https://github.com/manifoldmarkets/manifold/blob/main/common/src/calculate-cpmm.ts)
- **Linked MC Arbitrage**: [calculate-cpmm-arbitrage.ts](https://github.com/manifoldmarkets/manifold/blob/main/common/src/calculate-cpmm-arbitrage.ts)
