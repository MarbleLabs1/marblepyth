"""Pyth Network price feed ID lookup.

Feed IDs are stable hex identifiers for a price feed on Pyth's Hermes
service (https://hermes.pyth.network) and on-chain. Rather than hardcoding
them here (they're easy to get wrong and Pyth adds/renames feeds), this
resolves symbols to IDs at runtime against Hermes' own metadata endpoint and
caches the result for the process lifetime.

MRBL/USD isn't published on Pyth (no listing yet) — resolving it will raise
KeyError until Marble Blockchain has a Pyth-tracked market.
"""

from __future__ import annotations

import requests

HERMES_BASE_URL = "https://hermes.pyth.network"

_cache: dict[str, str] = {}


def resolve_feed_id(symbol: str) -> str:
    """Resolve a Pyth symbol (e.g. 'Crypto.SOL/USD') to its feed ID.

    Queries GET /v2/price_feeds on first lookup for a given symbol and
    caches the result; raises KeyError if Pyth has no matching feed.
    """
    if symbol in _cache:
        return _cache[symbol]

    query = symbol.split(".", 1)[-1]  # "Crypto.SOL/USD" -> "SOL/USD"
    response = requests.get(
        f"{HERMES_BASE_URL}/v2/price_feeds",
        params={"query": query, "asset_type": "crypto"},
        timeout=10,
    )
    response.raise_for_status()

    for entry in response.json():
        attributes = entry.get("attributes", {})
        if attributes.get("generic_symbol") == query or attributes.get("symbol") == symbol:
            feed_id = entry["id"]
            _cache[symbol] = feed_id
            return feed_id

    raise KeyError(f"No Pyth feed found for {symbol!r}")
