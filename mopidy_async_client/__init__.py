"""Async Mopidy Client via JSON/RPC Websocket interface"""

# Fork of https://github.com/ismailof/mopidy-json-client by ismailof
__author__ = 'svinerus (svinerus@gmail.com)'
__version__ = '0.4.1'

from .client import MopidyClient

__all__ = [
    'MopidyClient',
]
