"""
Utility functions for working with Manifold Markets API.

Usage:
    from utils import extract_comment_text, parallel_fetch_markets
"""

import json
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests

BASE_URL = "https://api.manifold.markets/v0"


# =============================================================================
# Comment Text Extraction
# =============================================================================


def extract_comment_text(content: dict | None) -> str:
    """
    Extract plain text from TipTap/ProseMirror JSON comment content.

    Manifold comments use a rich text format:
    {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "Hello "},
                {"type": "mention", "attrs": {"label": "username"}}
            ]}
        ]
    }

    This function extracts readable text from that structure.
    """
    if content is None:
        return ""

    def walk(node: Any) -> str:
        if isinstance(node, str):
            return node
        if isinstance(node, list):
            return "".join(walk(n) for n in node)
        if isinstance(node, dict):
            node_type = node.get("type", "")

            # Text node
            if node_type == "text":
                return node.get("text", "")

            # Mention (@user)
            if node_type == "mention":
                return f"@{node.get('attrs', {}).get('label', '')}"

            # Link
            if node_type == "link":
                # Links have marks on text nodes, just extract text
                pass

            # Image
            if node_type == "image":
                return f"[image: {node.get('attrs', {}).get('src', '')}]"

            # Container nodes (doc, paragraph, bulletList, etc.)
            if "content" in node:
                parts = [walk(c) for c in node["content"]]
                # Add newlines between certain block types
                if node_type in ("doc", "bulletList", "orderedList"):
                    return "\n".join(parts)
                if node_type == "listItem":
                    return "• " + " ".join(parts)
                return " ".join(parts)

            # Hard break
            if node_type == "hardBreak":
                return "\n"

        return ""

    return walk(content).strip()


# =============================================================================
# Parallel Fetching
# =============================================================================


def parallel_fetch_markets(market_ids: list[str], max_workers: int = 10) -> list[dict]:
    """
    Fetch multiple markets in parallel.

    Much faster than sequential fetching for large lists.

    Args:
        market_ids: List of market IDs to fetch
        max_workers: Number of parallel requests (default 10)

    Returns:
        List of market objects (order may differ from input)

    Example:
        markets = parallel_fetch_markets(["id1", "id2", "id3"])
    """
    results = []

    def fetch_one(market_id: str) -> dict | None:
        try:
            r = requests.get(f"{BASE_URL}/market/{market_id}", timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching {market_id}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, mid): mid for mid in market_ids}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results


def parallel_fetch_users(usernames: list[str], max_workers: int = 10) -> list[dict]:
    """
    Fetch multiple users in parallel.

    Args:
        usernames: List of usernames to fetch
        max_workers: Number of parallel requests (default 10)

    Returns:
        List of user objects
    """
    results = []

    def fetch_one(username: str) -> dict | None:
        try:
            r = requests.get(f"{BASE_URL}/user/{username}", timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, u): u for u in usernames}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    return results


def paginate_all(
    endpoint: str,
    params: dict | None = None,
    limit_per_page: int = 1000,
    max_pages: int = 100,
    id_field: str = "id",
) -> Iterator[dict]:
    """
    Paginate through an endpoint that supports 'before' cursor.

    Works with: /bets, /comments, /txns

    Args:
        endpoint: API endpoint (e.g., "/bets")
        params: Query parameters
        limit_per_page: Items per page (max 1000)
        max_pages: Maximum pages to fetch
        id_field: Field to use as cursor

    Yields:
        Individual items from each page

    Example:
        for bet in paginate_all("/bets", {"userId": "abc123"}):
            print(bet["createdTime"])
    """
    params = dict(params or {})
    params["limit"] = limit_per_page

    for _ in range(max_pages):
        r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
        r.raise_for_status()
        items = r.json()

        if not items:
            break

        yield from items

        if len(items) < limit_per_page:
            break

        # Use last item's ID as cursor
        params["before"] = items[-1][id_field]


# =============================================================================
# Batch Endpoints (use these when available)
# =============================================================================


def batch_fetch_market_probs(market_ids: list[str]) -> dict[str, float | dict]:
    """
    Fetch probabilities for multiple markets in one request.

    Uses /market-probs endpoint (up to 100 markets per request).

    Returns:
        Dict mapping market_id -> probability (binary) or answer_probs (MC)
    """
    results = {}

    # Batch into groups of 100
    for i in range(0, len(market_ids), 100):
        batch = market_ids[i : i + 100]
        params = [("ids[]", mid) for mid in batch]
        r = requests.get(f"{BASE_URL}/market-probs", params=params, timeout=30)
        r.raise_for_status()

        for item in r.json():
            mid = item.get("id")
            if "prob" in item:
                results[mid] = item["prob"]
            elif "answerProbs" in item:
                results[mid] = item["answerProbs"]

    return results


# =============================================================================
# Tips for Fast Fetching
# =============================================================================

FETCHING_TIPS = """
## Parallel Fetching Strategies

### When to use parallel fetching:
- Fetching many individual markets by ID
- Fetching many user profiles
- Any operation that makes many independent requests

### When to use batch endpoints instead:
- /market-probs: Fetch probabilities for up to 100 markets at once
- /markets-by-ids: Fetch full market data for multiple IDs (undocumented, root path)
- Supabase: For very large datasets (all markets, all users)

### Example: Fetching 500 markets

BAD (sequential, ~50 seconds):
    for mid in market_ids:
        market = requests.get(f"/market/{mid}").json()

BETTER (parallel, ~5 seconds):
    markets = parallel_fetch_markets(market_ids, max_workers=10)

BEST (batch endpoint, ~0.5 seconds):
    # If you only need probabilities:
    probs = batch_fetch_market_probs(market_ids)

    # Or use undocumented batch endpoint:
    r = requests.get("https://api.manifold.markets/markets-by-ids",
                     params=[("ids", mid) for mid in market_ids])

### Rate limits:
- 500 requests/minute per IP
- With 10 parallel workers, that's ~50 batches/minute
- For very large operations, add delays or use Supabase
"""

if __name__ == "__main__":
    # Demo: extract text from a sample comment
    sample = {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "mention", "attrs": {"id": "xxx", "label": "vluzko"}},
                    {"type": "text", "text": " Opus 4.5 is not close to SOTA at math!"},
                ],
            }
        ],
    }
    print("Sample comment extraction:")
    print(f"  Input: {json.dumps(sample)[:80]}...")
    print(f"  Output: {extract_comment_text(sample)}")

    print("\n" + FETCHING_TIPS)
