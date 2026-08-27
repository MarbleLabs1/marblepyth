"""Pyth Hermes client: fetch and normalize price feed updates."""

from __future__ import annotations

from dataclasses import dataclass

import requests

from .feed_ids import HERMES_BASE_URL, resolve_feed_id


@dataclass(frozen=True)
class PriceUpdate:
    symbol: str
    price: float
    confidence: float
    publish_time: int

    @classmethod
    def _from_hermes(cls, symbol: str, raw: dict) -> "PriceUpdate":
        price_data = raw["price"]
        exponent = price_data["expo"]
        scale = 10**exponent
        return cls(
            symbol=symbol,
            price=int(price_data["price"]) * scale,
            confidence=int(price_data["conf"]) * scale,
            publish_time=price_data["publish_time"],
        )


class PythFeed:
    """Polls Pyth Hermes for the latest price of a fixed set of symbols."""

    def __init__(self, symbols: list[str]):
        self.symbols = symbols
        self._feed_ids = {symbol: resolve_feed_id(symbol) for symbol in symbols}
        self._latest: dict[str, PriceUpdate] = {}

    def refresh(self) -> dict[str, PriceUpdate]:
        """Fetch the latest price for every tracked symbol in one request."""
        response = requests.get(
            f"{HERMES_BASE_URL}/v2/updates/price/latest",
            params={"ids[]": list(self._feed_ids.values())},
            timeout=10,
        )
        response.raise_for_status()

        id_to_symbol = {feed_id: symbol for symbol, feed_id in self._feed_ids.items()}
        for entry in response.json()["parsed"]:
            feed_id = entry["id"]
            symbol = id_to_symbol.get(feed_id)
            if symbol is None:
                continue
            self._latest[symbol] = PriceUpdate._from_hermes(symbol, entry)

        return dict(self._latest)

    def latest(self, symbol: str) -> PriceUpdate:
        """Return the most recently fetched price for a symbol, refreshing if needed."""
        if symbol not in self._latest:
            self.refresh()
        return self._latest[symbol]
