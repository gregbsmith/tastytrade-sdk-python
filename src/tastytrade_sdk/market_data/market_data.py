from typing import List, Callable, Optional

from injector import inject

from tastytrade_sdk.api import Api
from tastytrade_sdk.market_data.streamer_symbol_translation import StreamerSymbolTranslationsFactory
from tastytrade_sdk.market_data.subscription import Subscription
from tastytrade_sdk.market_data.models import Profile, Quote, Summary, Trade, Greeks


class MarketData:
    """
    Submodule for streaming market data
    """

    @inject
    def __init__(self, api: Api, streamer_symbol_translations_factory: StreamerSymbolTranslationsFactory):
        """@private"""
        self.__api = api
        self.__streamer_symbol_translations_factory = streamer_symbol_translations_factory

    def subscribe(self, symbols: List[str], on_profile: Optional[Callable[[Profile], None]] = None,
                  on_quote: Optional[Callable[[Quote], None]] = None,
                  on_summary: Optional[Callable[[Summary], None]] = None,
                  on_trade: Optional[Callable[[Trade], None]] = None,
                  on_greeks: Optional[Callable[[Greeks], None]] = None) -> Subscription:
        """
        Subscribe to live feed data
        :param symbols: Symbols to subscribe to. Can be across multiple instrument types.
        :param on_profile: Handle for `Profile` events
        :param on_quote: Handler for `Quote` events
        :param on_summary: Handler for `Summary` events
        :param on_trade: Handler for `Trade` events
        :param on_greeks: Handler for `Greeks` events
        """
        data = self.__api.get('/api-quote-tokens')['data']
        return Subscription(
            data['dxlink-url'],
            data['token'],
            self.__streamer_symbol_translations_factory.create(symbols),
            on_profile,
            on_quote,
            on_summary,
            on_trade,
            on_greeks
        )
