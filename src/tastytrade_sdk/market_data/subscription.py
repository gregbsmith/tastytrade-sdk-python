import datetime as dt
import logging
import threading
import time
from itertools import product
from math import floor
from typing import Callable, Optional

import ujson
from websockets.exceptions import ConnectionClosedOK
from websockets.sync.client import connect, ClientConnection

from tastytrade_sdk.exceptions import TastytradeSdkException, InvalidArgument
from tastytrade_sdk.market_data.models import Profile, Quote, Summary, Trade, Greeks
from tastytrade_sdk.market_data.streamer_symbol_translation import StreamerSymbolTranslations


class LoopThread(threading.Thread):
    def __init__(self, activity: Callable, timeout_seconds: int = 0):
        threading.Thread.__init__(self)
        self.__running = True
        self.__activity = activity
        self.__timeout_seconds = timeout_seconds
        super().start()

    def run(self):
        while self.__running:
            self.__activity()
            self.__pause()

    def __pause(self):
        if not self.__timeout_seconds:
            return
        start = time.time()
        while self.__running and time.time() - start <= self.__timeout_seconds:
            continue

    def stop(self):
        self.__running = False


class Subscription:
    __websocket: Optional[ClientConnection] = None
    __keepalive_thread: Optional[LoopThread]
    __receive_thread: Optional[LoopThread]
    __is_authorized: bool = False

    def __init__(self, url: str, token: str, streamer_symbol_translations: StreamerSymbolTranslations,
                 on_profile: Optional[Callable[[Profile], None]] = None,
                 on_quote: Optional[Callable[[Quote], None]] = None,
                 on_summary: Optional[Callable[[Summary], None]] = None,
                 on_trade: Optional[Callable[[Trade], None]] = None,
                 on_greeks: Optional[Callable[[Greeks], None]] = None):
        """@private"""

        if not (on_profile or on_quote or on_summary or on_trade or on_greeks):
            raise InvalidArgument('At least one feed event handler must be provided')

        self.__url = url
        self.__token = token
        self.__streamer_symbol_translations = streamer_symbol_translations
        self.__on_profile = on_profile
        self.__on_quote = on_quote
        self.__on_summary = on_summary
        self.__on_trade = on_trade
        self.__on_greeks = on_greeks

    def open(self) -> 'Subscription':
        """Start listening for feed events"""
        self.__websocket = connect(self.__url)
        self.__receive_thread = LoopThread(self.__receive)

        subscription_types = []
        if self.__on_profile:
            subscription_types.append('Profile')
        if self.__on_quote:
            subscription_types.append('Quote')
        if self.__on_summary:
            subscription_types.append('Summary')
        if self.__on_trade:
            subscription_types.append('Trade')
        if self.__on_greeks:
            subscription_types.append('Greeks')

        subscriptions = [{'symbol': s, 'type': t} for s, t in
                         product(self.__streamer_symbol_translations.streamer_symbols, subscription_types)]

        self.__send('SETUP', version='0.1', keepaliveTimeout=60, acceptKeepaliveTimeout=60)#, version='0.1-js/1.0.0')
        self.__send('AUTH', token=self.__token)
        while not self.__is_authorized:
            continue
        self.__send('CHANNEL_REQUEST', channel=1, service='FEED', parameters={'contract': 'AUTO'})
        self.__send('FEED_SUBSCRIPTION', channel=1, add=subscriptions)
        return self

    def close(self) -> None:
        """Close the stream connection"""
        if self.__keepalive_thread:
            self.__keepalive_thread.stop()
        if self.__receive_thread:
            self.__receive_thread.stop()
        if self.__websocket:
            self.__websocket.close()

    def __receive(self) -> None:
        if not self.__websocket:
            return
        try:
            message = ujson.loads(self.__websocket.recv())
        except ConnectionClosedOK:
            return
        _type = message['type']
        if _type == 'ERROR':
            raise StreamerException(message['error'], message['message'])
        if _type == 'SETUP': # also contains a more specific version number
            keepalive_interval = floor(message['keepaliveTimeout'] / 2)
            self.__keepalive_thread = LoopThread(lambda: self.__send('KEEPALIVE'), keepalive_interval)
        elif _type == 'AUTH_STATE': # userId is returned here on 'AUTHORIZED' message
            self.__is_authorized = message['state'] == 'AUTHORIZED'
        elif _type == 'FEED_DATA':
            for event in message['data']:
                self.__handle_feed_event(event)
        #elif _type == 'CHANNEL_OPENED': # Why is this returned twice?
            #pass # what is subFormat parameter returned here?
        #elif _type == 'FEED_CONFIG':
            #pass
        #elif _type == 'KEEPALIVE': # shouldn't be necessary since self.__keepalive_thread
            #self.__send('KEEPALIVE') # is created
        else:
            logging.debug('Unhandled message type: %s', _type)

    def __handle_feed_event(self, event: dict) -> None:
        event_type = event['eventType']
        original_symbol = self.__streamer_symbol_translations.get_original_symbol(event['eventSymbol'])
        if event_type == 'Profile' and self.__on_profile:
            self.__on_profile(Profile(
                symbol=original_symbol,
                description=event['description'],
                hi52wk=event['high52WeekPrice'],
                lo52wk=event['low52WeekPrice'],
                beta=event['beta'],
                earningsPerShare=event['earningsPerShare'],
                dividendFreq=event['dividendFrequency'],
                exDividendAmount=event['exDividendAmount'],
                shares=event['shares'],
                freeFloat=event['freeFloat']
            ))
        elif event_type == 'Quote' and self.__on_quote:
            self.__on_quote(Quote(
                symbol=original_symbol,
                bid_price=event['bidPrice'],
                bid_size=event['bidSize'],
                bid_exchange_code=event['bidExchangeCode'],
                ask_price=event['askPrice'],
                ask_size=event['askSize'],
                ask_exchange_code=event['askExchangeCode']
            ))
        elif event_type == 'Summary' and self.__on_summary:
            self.__on_summary(Summary(
                symbol=original_symbol,
                eventSymbol=event['eventSymbol'],
                dayId=event['dayId'],
                dayOpen=event['dayOpenPrice'],
                dayHigh=event['dayHighPrice'],
                dayLow=event['dayLowPrice'],
                dayClose=event['dayClosePrice'],
                prevDayId=event['prevDayId'],
                prevClose=event['prevDayClosePrice'],
                prevDayVolume=event['prevDayVolume'],
                openInterest=event['openInterest']
            ))
        elif event_type == 'Trade' and self.__on_trade:
            self.__on_trade(Trade(
                symbol=original_symbol,
                eventSymbol=event['eventSymbol'],
                # necessary to convert to sec then datetime
                time=dt.datetime.utcfromtimestamp(event['time'] / 1000),
                # ^^^ very important that this step is done once
                # and nowhere else ***
                sequence=event['sequence'],
                exchangeCode=event['exchangeCode'],
                price=event['price'],
                change=event['change'],
                size=event['size'],
                extendedTradingHours=event['extendedTradingHours'],
                dayId=event['dayId'],
                dayVolume=event['dayVolume'],
                dayTurnover=event['dayTurnover']
            ))
        elif event_type == 'Greeks' and self.__on_greeks:
            self.__on_greeks(Greeks(
                symbol=original_symbol,
                time=event['time'],
                price=event['price'],
                volatility=event['volatility'],
                delta=event['delta'],
                gamma=event['gamma'],
                theta=event['theta'],
                vega=event['vega'],
                rho=event['rho']
            ))
        else:
            logging.debug('Unhandled feed event type %s for symbol %s', event_type, original_symbol)

    def __send(self, _type: str, channel: Optional[int] = 0, **kwargs) -> None:
        self.__websocket.send(ujson.dumps({
            **{'type': _type, 'channel': channel},
            **kwargs
        }))


class StreamerException(TastytradeSdkException):
    def __init__(self, error: str, message: str):
        super().__init__(f'{error}: {message}')
