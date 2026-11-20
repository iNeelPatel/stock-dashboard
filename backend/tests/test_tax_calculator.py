import pytest
from decimal import Decimal
from backend.app.core.tax_calculator import calculate_charges

def test_delivery_buy_charges():
    # Buy 100 shares of Reliance at ₹2500 = ₹2,50,000 turnover
    charges = calculate_charges(
        direction="BUY",
        order_mode="INVESTMENT",
        quantity=100,
        price=Decimal("2500.00"),
        is_intraday=False
    )
    assert charges.turnover == Decimal("250000.00")
    # STT: 0.1% of 2,50,000 = 250.00
    assert charges.stt == Decimal("250.00")
    # Stamp duty: 0.015% of 2,50,000 = 37.50
    assert charges.stamp_duty == Decimal("37.50")
    # Net amount must be turnover + total_charges
    assert charges.net_amount == charges.turnover + charges.total_charges
    assert charges.total_charges > Decimal("287.50")

def test_delivery_sell_charges():
    # Sell 100 shares at ₹2600 = ₹2,60,000 turnover
    charges = calculate_charges(
        direction="SELL",
        order_mode="INVESTMENT",
        quantity=100,
        price=Decimal("2600.00"),
        is_intraday=False
    )
    assert charges.turnover == Decimal("260000.00")
    # STT on sell: 0.1% = 260.00
    assert charges.stt == Decimal("260.00")
    # Stamp duty on sell is 0.00
    assert charges.stamp_duty == Decimal("0.00")
    # Net amount on sell must be turnover - total_charges
    assert charges.net_amount == charges.turnover - charges.total_charges

def test_intraday_buy_and_sell():
    buy_charges = calculate_charges(
        direction="BUY",
        order_mode="TRADING",
        quantity=100,
        price=Decimal("1000.00"),
        is_intraday=True
    )
    # Intraday buy: no STT
    assert buy_charges.stt == Decimal("0.00")
    # Intraday buy: stamp duty = 0.003% of 100,000 = 3.00
    assert buy_charges.stamp_duty == Decimal("3.00")

    sell_charges = calculate_charges(
        direction="SELL",
        order_mode="TRADING",
        quantity=100,
        price=Decimal("1020.00"),
        is_intraday=True
    )
    # Intraday sell: STT = 0.025% of 102,000 = 25.50
    assert sell_charges.stt == Decimal("25.50")
    # Stamp duty on sell is 0
    assert sell_charges.stamp_duty == Decimal("0.00")
