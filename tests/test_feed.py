from marblepyth.feed import PriceUpdate


def test_price_update_scales_by_exponent():
    raw = {"price": {"price": "123456", "conf": "10", "expo": -2, "publish_time": 1700000000}}
    update = PriceUpdate._from_hermes("Crypto.SOL/USD", raw)

    assert update.price == 1234.56
    assert update.confidence == 0.1
    assert update.publish_time == 1700000000
