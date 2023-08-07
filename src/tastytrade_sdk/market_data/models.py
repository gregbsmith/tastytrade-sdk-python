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
        eventSymbol
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
    hi52wk: Optional[float]
    lo52wk: Optional[float]
    beta: Optional[float]
    earningsPerShare: Optional[float]
    dividendFreq: Optional[float]
    exDividendAmount: Optional[float]
    shares: Optional[float] # outstanding shares
    freeFloat: Optional[float]
    def __init__(self, symbol: str, description: str, hi52wk: NullableFloatStr, lo52wk: NullableFloatStr,
                 beta: NullableFloatStr, earningsPerShare: NullableFloatStr, dividendFreq: NullableFloatStr,
                 exDividendAmount: NullableFloatStr, shares: NullableFloatStr, freeFloat: NullableFloatStr):
        self.symbol = symbol
        self.description = description
        self.hi52wk = _float(hi52wk)
        self.lo52wk = _float(lo52wk)
        self.beta = _float(beta)
        self.earningsPerShare = _float(earningsPerShare)
        self.dividendFreq = _float(dividendFreq)
        self.exDividendAmount = _float(exDividendAmount)
        self.shares = _float(shares)
        self.freeFloat = _float(freeFloat)


@dataclass
class Quote:
    """ Attributes not handled here:
        """
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
class Summary:
    """ Attributes not handled here:
        dayClosePriceType
        prevDayClosePriceType
        """
    symbol: str
    eventSymbol: str
    dayId: int
    dayOpen: Optional[float]
    dayHigh: Optional[float]
    dayLow: Optional[float]
    dayClose: Optional[float]
    prevDayId: int
    prevClose: Optional[float]
    prevDayVolume: Optional[float]
    openInterest: int

    def __init__(self, symbol: str, eventSymbol: str, dayId: int, dayOpen: NullableFloatStr, dayHigh:NullableFloatStr,
                 dayLow: NullableFloatStr, dayClose: NullableFloatStr, prevDayId: int, prevClose: NullableFloatStr,
                 prevDayVolume: NullableFloatStr, openInterest: int):
        self.symbol = symbol
        self.eventSymbol = eventSymbol
        self.dayId = dayId
        self.dayOpen = _float(dayOpen)
        self.dayHigh = _float(dayHigh)
        self.dayLow = _float(dayLow)
        self.dayClose = _float(dayClose)
        self.prevDayId = prevDayId
        self.prevClose = _float(prevClose)
        self.prevDayVolume = _float(prevDayVolume)
        self.openInterest = openInterest

@dataclass
class Trade:
    """ Attributes not handled here:
        timeNanoPart (it always seems to be 0)
        tickDirection
        sizeAsDouble
        dayVolumeAsDouble
        """
    symbol: str
    eventSymbol: str
    # seconds since dt.datetime.utcfromtimestamp(0)
    time: int
    sequence: int
    exchangeCode: str
    price: Optional[float]
    change: Optional[float]
    size: int
    extendedTradingHours: bool
    dayId: int
    dayVolume: int
    dayTurnover: Optional[float]
    def __init__(self, symbol: str, eventSymbol: str, time: int, sequence: int, exchangeCode: str,
                 price: NullableFloatStr, change: NullableFloatStr, size: int, extendedTradingHours: bool,
                 dayId: int, dayVolume: int, dayTurnover: NullableFloatStr):
        self.symbol = symbol
        self.eventSymbol = eventSymbol
        self.time = time
        self.sequence = sequence
        self.exchangeCode = exchangeCode
        self.price = _float(price)
        self.change = _float(change)
        self.size = size
        self.extendedTradingHours = extendedTradingHours
        self.dayId = dayId
        self.dayVolume = dayVolume
        self.dayTurnover = _float(dayTurnover)

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
