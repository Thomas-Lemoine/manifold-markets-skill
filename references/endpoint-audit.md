# Endpoint Audit

Complete list of Manifold API endpoints with status and notes.

**Contents:** [Markets](#markets) · [Betting](#betting) · [Users](#users) · [Social/Comments](#social--comments) · [Groups/Topics](#groups--topics) · [Mana/Transactions](#mana--transactions) · [Feed/Discovery](#feed--discovery) · [DMs](#direct-messages) · [Follows](#follows) · [Posts](#posts-blog-like-feature) · [Admin](#-admin--internal-only) · [Summary](#summary)

**Legend:**
- ✅ Documented in skill
- 📝 Should add to skill
- ⚠️ Niche/advanced (document briefly)
- 🔒 Admin/internal (skip or note as off-limits)
- ❓ Unknown purpose (needs investigation)

> **Root-path endpoints:** Many real endpoints live at `https://api.manifold.markets/<name>` (no `/v0/` prefix) — e.g. `unresolve`, `markets-by-ids`, `edit-answer-cpmm`, `search-users`. They are **not** listed at `docs.manifold.markets/api`. If a `/v0/...` probe returns 404, also try the root path before concluding the feature doesn't exist; the rows below tagged "(root path)" mark the known cases.

---

## Markets

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `market/:id` | GET | ✅ | Full market object |
| `market/:id/lite` | GET | 📝 | Lightweight fetch (fewer fields, faster) |
| `market/:id/prob` | GET | ✅ | Current probability |
| `market-probs` | GET | ✅ | Batch probabilities |
| `markets-by-ids` | GET | ✅ | Batch fetch markets (root path) |
| `slug/:slug` | GET | ✅ | Fetch by slug |
| `markets` | GET | ✅ | List/paginate markets |
| `search-markets` | GET | ✅ | Search markets |
| `search-markets-full` | GET | 📝 | Search with full market objects (not lite) |
| `recent-markets` | GET | 📝 | Recently created/updated markets |
| `market/:contractId/groups` | GET | ✅ | Groups a market belongs to |
| `market/:contractId/answers` | GET | 📝 | All answers for MC market |
| `answer/:answerId` | GET | 📝 | Single answer details |
| `market/:id/positions` | GET | ✅ | Positions in market |
| `get-related-markets` | GET | ✅ | Similar markets (root path) |
| `get-related-markets-by-group` | GET | 📝 | Related by shared group |
| `get-market-context` | GET | ❓ | Market context (unclear purpose) |
| `get-market-props` | GET | ⚠️ | Internal market properties |
| `get-contract-voters` | GET | 📝 | Poll voters |
| `get-contract-option-voters` | GET | 📝 | Poll option voters |
| `market` | POST | ✅ | Create market |
| `market/:contractId/update` | POST | ✅ | Update market |
| `market/:contractId/close` | POST | ✅ | Close market |
| `market/:contractId/resolve` | POST | ✅ | Resolve market |
| `market/:contractId/add-liquidity` | POST | ✅ | Add liquidity |
| `market/:contractId/remove-liquidity` | POST | ✅ | Remove liquidity |
| `market/:contractId/add-bounty` | POST | ✅ | Add bounty |
| `market/:contractId/award-bounty` | POST | ✅ | Award bounty |
| `market/:contractId/group` | POST | ✅ | Add/remove from group |
| `market/:contractId/answer` | POST | ✅ | Add answer to MC |
| `edit-answer-cpmm` | POST | ✅ | Edit answer text/color on cpmm-multi-1 MC (root path) |
| `market/:contractId/block` | POST | ✅ | Block market |
| `market/:contractId/unblock` | POST | ✅ | Unblock market |
| `unresolve` | POST | ✅ | Unresolve market (root path, creator only) |
| `save-market-draft` | POST | ⚠️ | Save draft (UI feature) |
| `delete-market-draft` | POST | ⚠️ | Delete draft |

---

## Betting

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `bet` | POST | ✅ | Place bet |
| `bet/cancel/:betId` | POST | ✅ | Cancel limit order |
| `multi-bet` | POST | ✅ | Bet on multiple MC answers |
| `multi-sell` | POST | ✅ | Sell multiple MC positions |
| `market/:contractId/sell` | POST | ✅ | Sell shares |
| `bets` | GET | ✅ | Get bets (filterable) |
| `user/:username/bets` | GET | 📝 | User's bets (alternative path) |
| `bet-points` | GET | ❓ | Unknown - possibly bet analytics |
| `unique-bet-group-count` | GET | 📝 | Unique bettor count for market |
| `get-user-limit-orders-with-contracts` | GET | 📝 | Open limit orders with market data |

---

## Users

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `me` | GET | ✅ | Authenticated user |
| `me/private` | GET | ⚠️ | Private user data (sensitive) |
| `get-user-private-data` | GET | ⚠️ | Private data (sensitive) |
| `user/:username` | GET | ✅ | User by username |
| `user/:username/lite` | GET | 📝 | Lightweight user fetch |
| `user/by-id/:id` | GET | ✅ | User by ID |
| `user/by-id/:id/lite` | GET | 📝 | Lightweight by ID |
| `users/by-id` | GET | ✅ | Batch fetch users |
| `users/by-id/balance` | GET | 📝 | Batch user balances only |
| `users` | GET | ✅ | List users |
| `search-users` | GET | ✅ | Search users (root path) |
| `get-user-portfolio` | GET | ✅ | Live portfolio |
| `get-user-portfolio-history` | GET | ✅ | Portfolio history |
| `get-user-contract-metrics-with-contracts` | GET | ✅ | Positions with contracts |
| `get-user-last-active-time` | GET | ✅ | Last activity (root path) |
| `get-balance-changes` | GET | ✅ | Balance history (root path) |
| `get-user-achievements` | GET | ✅ | User achievements (trade count) |
| `get-user-calibration` | GET | ✅ | Profit, volume, calibration, Sharpe ratio |
| `get-monthly-bets-2025` | GET | ⚠️ | 2025-specific stats |
| `get-max-min-profit-2025` | GET | ⚠️ | 2025-specific stats |
| `get-user-info` | GET | ❓ | Unknown - possibly duplicate |
| `me/update` | POST | 📝 | Update own profile |
| `me/delete` | POST | ⚠️ | Delete account (destructive!) |
| `me/private/update` | POST | ⚠️ | Update private settings |
| `user/by-id/:id/block` | POST | 📝 | Block a user |
| `user/by-id/:id/unblock` | POST | 📝 | Unblock a user |
| `update-notif-settings` | POST | 📝 | Notification preferences |
| `set-push-token` | POST | ⚠️ | Mobile push token (app-specific) |
| `refer-user` | POST | ⚠️ | Referral system |

---

## Social / Comments

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `comments` | GET | ✅ | Get comments |
| `user-comments` | GET | 📝 | User's comments (alternative) |
| `comment-threads` | GET | ✅ | Threaded comments |
| `comment-thread` | GET | ✅ | Single thread |
| `get-best-comments` | GET | 📝 | Top comments |
| `comment-reactions` | GET | 📝 | Reactions on comments |
| `comment` | POST | ✅ | Post comment |
| `hide-comment` | POST | ✅ | Hide/delete comment |
| `pin-comment` | POST | 📝 | Pin comment (creator) |
| `react` | POST | ✅ | Like/unlike (root path) |

---

## Groups / Topics

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `groups` | GET | ✅ | List groups |
| `group/:slug` | GET | ✅ | Group by slug |
| `group/by-id/:id` | GET | ✅ | Group by ID |
| `group/:slug/groups` | GET | 📝 | Subgroups |
| `group/:slug/dashboards` | GET | ⚠️ | Group dashboards |
| `group/by-id/:id/groups` | GET | 📝 | Subgroups by ID |
| `group/by-id/:id/markets` | GET | 📝 | Markets in group |
| `search-groups` | GET | 📝 | Search groups |
| `search-my-groups` | GET | 📝 | Search user's followed groups |
| `get-groups-with-top-contracts` | GET | 📝 | Groups with most popular markets |
| `get-followed-groups` | GET | ✅ | User's followed groups |
| `get-interesting-groups-from-views` | GET | ⚠️ | ML-based suggestions |
| `group/:slug/delete` | POST | ⚠️ | Delete group (owner only) |
| `group/by-id/:id/delete` | POST | ⚠️ | Delete group by ID |
| `group/:slug/block` | POST | ⚠️ | Block group |
| `group/:slug/unblock` | POST | ⚠️ | Unblock group |
| `group/by-id/:topId/group/:bottomId` | POST | ❓ | Unknown - group hierarchy? |

---

## Mana / Transactions

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `managrams` | GET | ✅ | Mana transfers |
| `txns` | GET | ✅ | All transactions |
| `get-mana-supply` | GET | ✅ | Platform mana stats (root path) |
| `get-txn-summary-stats` | GET | 📝 | Transaction statistics |
| `get-mana-summary-stats` | GET | 📝 | Mana statistics |
| `get-active-user-mana-stats` | GET | ⚠️ | Active user mana (internal?) |
| `get-next-loan-amount` | GET | ✅ | Available loan (root path) |
| `get-cashouts` | GET | ⚠️ | Cashout history |
| `managram` | POST | ✅ | Send mana |
| `manalink` | POST | 🔒 | Create manalink (admin only) |
| `donate` | POST | ✅ | Donate mana |
| `convert-sp-to-mana` | POST | ✅ | Convert streak points |
| `convert-cash-to-mana` | POST | ⚠️ | Convert cash (if cash exists) |
| `request-loan` | POST | ✅ | Claim daily loan (root path) |

---

## Feed / Discovery

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-feed` | GET | ✅ | Personalized feed (root path) |
| `get-site-activity` | GET | 📝 | Global activity feed |
| `headlines` | GET | 📝 | News headlines |
| `politics-headlines` | GET | 📝 | Politics headlines |
| `get-notifications` | GET | ✅ | User notifications (root path) |
| `fetch-link-preview` | GET | ⚠️ | Link preview generation |
| `get-dashboard-from-slug` | GET | ⚠️ | Dashboard fetch |
| `get-seen-market-ids` | GET | ⚠️ | Tracking seen markets |
| `record-contract-view` | POST | 🔒 | Analytics tracking |
| `record-comment-view` | POST | 🔒 | Analytics tracking |
| `record-contract-interaction` | POST | 🔒 | Analytics tracking |
| `mark-all-notifications-new` | POST | ⚠️ | Reset notification state |

---

## Direct Messages

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-channel-memberships` | GET | ✅ | DM channels (root path) |
| `get-channel-messages` | GET | ✅ | Read DMs (root path) |
| `get-channel-seen-time` | GET | 📝 | Last read time |
| `set-channel-seen-time` | POST | ✅ | Mark as read (root path) |
| `create-public-chat-message` | POST | ✅ | Send DM message (confusing name, but this IS for DMs) |

---

## Follows

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `follow-contract` | POST | ✅ | Follow/unfollow market |

---

## Posts (Blog-like feature)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-posts` | GET | 📝 | List posts |
| `post` | POST | ⚠️ | Create post (deprecated?) |
| `create-post` | POST | 📝 | Create post |
| `update-post` | POST | 📝 | Update post |
| `create-post-comment` | POST | 📝 | Comment on post |
| `update-post-comment` | POST | 📝 | Update post comment |
| `edit-post-comment` | POST | 📝 | Edit post comment |
| `follow-post` | POST | 📝 | Follow post |

---

## Leagues

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `leagues` | GET | 📝 | League info (may not work via API) |

---

## Sports Integration

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-sports-games` | GET | ⚠️ | Sports data |
| `check-sports-event` | GET | ⚠️ | Verify sports event |

---

## AI Features

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `generate-ai-market-suggestions` | POST | ⚠️ | AI market ideas |
| `generate-ai-description` | POST | ⚠️ | AI descriptions |
| `generate-ai-answers` | POST | ⚠️ | AI answer suggestions |
| `generate-ai-numeric-ranges` | POST | ⚠️ | AI numeric ranges |
| `generate-ai-date-ranges` | POST | ⚠️ | AI date ranges |
| `generate-concise-title` | POST | ⚠️ | AI title shortening |
| `get-close-date` | POST | ⚠️ | AI close date suggestion |
| `infer-numeric-unit` | POST | ⚠️ | AI unit inference |
| `regenerate-numeric-midpoints` | POST | ⚠️ | Regenerate buckets |
| `regenerate-date-midpoints` | POST | ⚠️ | Regenerate date buckets |
| `check-poll-suggestion` | POST | ⚠️ | Check poll viability |

---

## Tasks (Todo system)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-tasks` | GET | ⚠️ | Internal task system |
| `get-categories` | GET | ⚠️ | Task categories |
| `create-task` | POST | ⚠️ | Create task |
| `update-task` | POST | ⚠️ | Update task |
| `create-category` | POST | ⚠️ | Create category |
| `update-category` | POST | ⚠️ | Update category |

---

## Boosts (Promotion)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `purchase-boost` | POST | ⚠️ | Buy market boost |
| `get-boost-analytics` | GET | ⚠️ | Boost performance |

---

## Predictle (Word game)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-predictle-markets` | GET | ⚠️ | Predictle game markets |
| `get-predictle-result` | GET | ⚠️ | Game results |
| `save-predictle-result` | POST | ⚠️ | Save game result |

---

## Clarifications (Market updates)

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-pending-clarifications` | GET | 📝 | Pending market clarifications |
| `apply-pending-clarification` | POST | 📝 | Apply clarification |
| `cancel-pending-clarification` | POST | 📝 | Cancel clarification |

---

## Partner System

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `get-partner-stats` | GET | ⚠️ | Partner statistics |

---

## Integrations

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `save-twitch` | POST | ⚠️ | Twitch integration |
| `set-news` | POST | ⚠️ | News preferences |

---

## 🔒 Admin / Internal Only

These endpoints require admin privileges or are for internal use:

| Endpoint | Method | Notes |
|----------|--------|-------|
| `refresh-all-clients` | POST | Force client refresh |
| `toggle-system-trading-status` | POST | Enable/disable trading globally |
| `recover-user` | POST | Recover deleted user |
| `admin-delete-user` | POST | Admin user deletion |
| `anonymize-user` | POST | GDPR anonymization |
| `createuser` | POST | Internal user creation |
| `super-ban-user` | POST | Platform-wide ban |
| `get-mod-reports` | GET | Moderation queue |
| `update-mod-report` | POST | Handle report |
| `dismiss-user-report` | POST | Dismiss report |
| `admin-search-users-by-email` | GET | Email lookup |
| `admin-get-related-users` | GET | Find alt accounts |

---

## 🔒 GIDX (Identity Verification)

These are for identity verification (sweepstakes compliance):

| Endpoint | Method | Notes |
|----------|--------|-------|
| `get-verification-status-gidx` | GET | KYC status |
| `get-monitor-status-gidx` | GET | Monitoring status |
| `get-checkout-session-gidx` | GET | Checkout session |
| `get-verification-documents-gidx` | GET | KYC documents |
| `register-gidx` | POST | Start KYC |
| `complete-checkout-session-gidx` | POST | Complete checkout |
| `complete-cashout-session-gidx` | POST | Complete cashout |
| `complete-cashout-request` | POST | Finalize cashout |
| `upload-document-gidx` | POST | Upload KYC doc |

---

## 🔒 Phone Verification

| Endpoint | Method | Notes |
|----------|--------|-------|
| `request-otp` | GET | Request OTP code |
| `verify-phone-number` | GET/POST | Verify phone |

---

## 🔒 In-App Purchases

| Endpoint | Method | Notes |
|----------|--------|-------|
| `validateIap` | POST | Validate iOS/Android purchase |

---

## Summary

| Status | Count | Action |
|--------|-------|--------|
| ✅ Documented | ~47 | Already in skill |
| 📝 Should add | ~33 | Add to skill |
| ⚠️ Niche/advanced | ~40 | Brief mention or skip |
| 🔒 Admin/internal | ~25 | Note as off-limits |
| ❓ Unknown | ~5 | Needs investigation |

**Recent additions:** `get-user-calibration` (Sharpe ratio), `get-user-achievements` (trade count)
