from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel
from backend.app.core.config import settings

class ChargeBreakdown(BaseModel):
    turnover: Decimal
    brokerage: Decimal
    stt: Decimal
    exchange_charges: Decimal
    gst: Decimal
    stamp_duty: Decimal
    sebi_charges: Decimal
    total_charges: Decimal
    net_amount: Decimal  # Buy: turnover + total_charges; Sell: turnover - total_charges

def round_curr(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calculate_charges(
    direction: str,  # "BUY" or "SELL"
    order_mode: str,  # "INVESTMENT" (Delivery) or "TRADING" (Intraday/Swing)
    quantity: int,
    price: Decimal,
    is_intraday: bool = False
) -> ChargeBreakdown:
    direction = direction.upper()
    qty_dec = Decimal(quantity)
    turnover = round_curr(qty_dec * price)

    if is_intraday:
        # Intraday brokerage: lower of ₹20 or 0.03%
        raw_brokerage = turnover * settings.INTRADAY_BROKERAGE_RATE
        brokerage = min(settings.INTRADAY_BROKERAGE_FLAT, raw_brokerage)
        
        # STT: 0.025% on Sell only
        stt = round_curr(turnover * settings.INTRADAY_STT_RATE) if direction == "SELL" else Decimal("0.00")
        
        # Stamp Duty: 0.003% on Buy only
        stamp_duty = round_curr(turnover * settings.INTRADAY_STAMP_DUTY_RATE) if direction == "BUY" else Decimal("0.00")
    else:
        # Delivery brokerage: ₹0 (or flat if configured)
        brokerage = settings.DELIVERY_BROKERAGE_FLAT
        
        # STT: 0.1% on both Buy and Sell
        stt = round_curr(turnover * settings.DELIVERY_STT_RATE)
        
        # Stamp Duty: 0.015% on Buy only
        stamp_duty = round_curr(turnover * settings.DELIVERY_STAMP_DUTY_RATE) if direction == "BUY" else Decimal("0.00")

    # Exchange transaction charges (NSE equity: ~0.00345%)
    exchange_charges = round_curr(turnover * settings.DELIVERY_EXCHANGE_TXN_RATE)

    # SEBI turnover charges (₹10 per crore = 0.0001%)
    sebi_charges = round_curr(turnover * settings.DELIVERY_SEBI_CHARGES_RATE)
    if sebi_charges == Decimal("0.00") and turnover > Decimal("100.00"):
        sebi_charges = Decimal("0.01")  # Min fractional charge if turnover > 100

    # GST: 18% on (Brokerage + Exchange Txn + SEBI)
    gst_taxable = brokerage + exchange_charges + sebi_charges
    gst = round_curr(gst_taxable * settings.DELIVERY_GST_RATE)

    total_charges = round_curr(brokerage + stt + exchange_charges + gst + stamp_duty + sebi_charges)

    if direction == "BUY":
        net_amount = round_curr(turnover + total_charges)
    else:
        net_amount = round_curr(turnover - total_charges)

    return ChargeBreakdown(
        turnover=turnover,
        brokerage=round_curr(brokerage),
        stt=stt,
        exchange_charges=exchange_charges,
        gst=gst,
        stamp_duty=stamp_duty,
        sebi_charges=sebi_charges,
        total_charges=total_charges,
        net_amount=net_amount
    )
