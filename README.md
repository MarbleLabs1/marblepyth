# marblepyth

Python client for pulling [Pyth Network](https://pyth.network) price feeds
into Marble Blockchain services — the DEX, wallet, and any contract that
needs a real-time price reference instead of trusting a single exchange.

Pyth already backs the project's existing Solana bridge, so this reuses that
same trust source rather than adding a new price oracle to audit.

## What it does

- Subscribes to Pyth price feed accounts over Hermes (Pyth's off-chain
  price service) for the pairs Marble cares about (SOL/USD, MRBL/USD once
  listed, and whatever the DEX adds).
- Normalizes each update into a plain `PriceUpdate` (price, confidence
  interval, exponent, publish time) so callers don't touch raw Pyth account
  layouts.
- Exposes a small polling and streaming API so `marble_dex_app.py` and the
  wallet can ask for "latest price" or subscribe to a feed.

## Install

```sh
pip install -r requirements.txt
```

## Usage

```python
from marblepyth import PythFeed

feed = PythFeed(["Crypto.SOL/USD"])
price = feed.latest("Crypto.SOL/USD")
print(price.price, "+/-", price.confidence)
```

## Status

Early — the client wraps Pyth's Hermes REST/SSE endpoints today; a direct
on-chain read path (for contracts that can't make HTTP calls) is planned
once the Marble Blockchain VM supports it.
