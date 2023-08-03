from dataclasses import dataclass
from math import isnan
from typing import Optional, Union

NullableFloatStr = Optional[Union[float, str]]


def _float(value: NullableFloatStr) -> Optional[float]:
    if isinstance(value, str):
        return float(value) if value.isnumeric() else None
    if value is None:
        return None
    return None if isnan(value) else value


@dataclass
class Profile:
    """ Attributes not handled here:
        shortSaleRestriction
        tradingStatus
        statusReason
        haltStartTime
        haltEndTime
        highLimitPrice
        lowLimitPrice
        """
    symbol: str
    description: str
    hi52wk: float
    lo52wk: float
    beta: float
    earningsPerShare: float
    dividendFreq: float
    exDividendAmount: float
    shares: float # outstanding shares
    freeFloat: float
    def __init__(self, symbol: str, description: str, hi52wk: float, lo52wk: float,
                 beta: float, earningsPerShare: float, dividendFreq: float,
                 exDividendAmount: float, shares: float, freeFloat: float):
        self.symbol = symbol
        self.description = description
        self.hi52wk = hi52wk
        self.lo52wk = lo52wk
        self.beta = beta
        self.earningsPerShare = earningsPerShare
        self.dividendFreq = dividendFreq
        self.exDividendAmount = exDividendAmount
        self.shares = shares
        self.freeFloat = freeFloat


@dataclass
class Quote:
    symbol: str
    bid_price: Optional[float]
    bid_size: Optional[float]
    bid_exchange_code: Optional[str]
    ask_price: Optional[float]
    ask_size: Optional[float]
    ask_exchange_code: Optional[str]

    def __init__(self, symbol: str, bid_price: NullableFloatStr, bid_size: NullableFloatStr,
                 bid_exchange_code: Optional[str], ask_price: NullableFloatStr, ask_size: NullableFloatStr,
                 ask_exchange_code: Optional[str]):
        """@private"""
        self.symbol = symbol
        self.bid_price = _float(bid_price)
        self.bid_size = _float(bid_size)
        self.bid_exchange_code = bid_exchange_code
        self.ask_price = _float(ask_price)
        self.ask_size = _float(ask_size)
        self.ask_exchange_code = ask_exchange_code

@dataclass
class Greeks:
    symbol: str
    time: int
    price: Optional[float]
    volatility: Optional[float]
    delta: Optional[float]
    gamma: Optional[float]
    theta: Optional[float]
    rho: Optional[float]
    vega: Optional[float]

    def __init__(self, symbol: str, time: int, price: NullableFloatStr, volatility: NullableFloatStr,
                 delta: NullableFloatStr, gamma: NullableFloatStr, theta: NullableFloatStr, rho: NullableFloatStr,
                 vega: NullableFloatStr):
        """@private"""
        self.symbol = symbol
        self.time = time
        self.price = _float(price)
        self.volatility = _float(volatility)
        self.delta = _float(delta)
        self.gamma = _float(gamma)
        self.theta = _float(theta)
        self.rho = _float(rho)
        self.vega = _float(vega)
