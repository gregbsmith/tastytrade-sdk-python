[![PyPI](https://img.shields.io/pypi/v/tastytrade-sdk)](https://pypi.org/project/tastytrade-sdk/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/tastytrade-sdk)](https://pypi.org/project/tastytrade-sdk/)

# tastytrade-sdk-python

A python wrapper around the [tastytrade open API](https://developer.tastytrade.com/)

## Documentation

For users: [Official Documentation](https://tastytrade.github.io/tastytrade-sdk-python)

For contributors: [Developer Guide](./docs/contributors/README.md)

TODO:
- [x] Switch to new multiplexors for market data streaming: https://developer.tastytrade.com/streaming-market-data/
	- must change:
		models.py
		market_data.py
		subscription.py

How to get your remember-token:

tasty.api.\_Api\_\_session.\_RequestsSession\_\_session.params['remember-token']
