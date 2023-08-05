from injector import Injector

from tastytrade_sdk.config import Config
from tastytrade_sdk.api import Api, RequestsSession
from tastytrade_sdk.market_data.market_data import MarketData


class Tastytrade:
    """
    The SDK's top-level class
    """

    def __init__(self, sandbox=False):
        """
        :param sandbox: allow the user to specify sandbox mode to change api base url to
        cert url, which is 'api.cert.tastyworks.com'
        """
        api_base_url = 'api.tastyworks.com'
        if sandbox:
            api_base_url = 'api.cert.tastyworks.com'
        def configure(binder):
            binder.bind(Config, to=Config(api_base_url=api_base_url))

        self.__container = Injector(configure)

    def login(
            self,
            login: str,
            password: str=None,
            remember_token: str=None,
            remember_me: bool=True) -> 'Tastytrade':
        """
        Initialize a logged-in session
        """
        if not remember_token:
            self.__container.get(RequestsSession).login(login,
                                                        password=password, 
                                                        remember_me=remember_me)
        elif not password:
            self.__container.get(RequestsSession).login(login,
                                                        remember_token=remember_token,
                                                        remember_me=remember_me)
        else:
            print("Error: failed to log in. You must provide a password or valid remember token to log in.")
        return self

    def logout(self) -> None:
        """
        End the session
        """
        self.api.delete('/sessions')

    @property
    def market_data(self) -> MarketData:
        """
        Access the MarketData submodule
        """
        return self.__container.get(MarketData)

    @property
    def api(self) -> Api:
        """
        Access the Api submodule
        """
        return self.__container.get(Api)
