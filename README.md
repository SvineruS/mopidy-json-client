# Mopidy-Async-Client 

### Fork of [Mopidy-json-client](https://github.com/ismailof/mopidy-json-client), but from scratch and async


Async Mopidy Client via JSON/RPC Websocket interface

## Usage

mopidy-async-client provides a main class `MopidyClient`, which manages the connection and methods to the Mopidy Server.
Use the `bind_event` function to subscribe to mopidy events.

```python
from mopidy_async_client import MopidyClient


async def main():
    async with MopidyClient() as mopidy:
        mopidy.bind_event('track_playback_started', print_track_info)
        await mopidy.playback.play()
```

## Installation

 `pip install mopidy-async-client`


## References
- [Mopidy Core API](https://mopidy.readthedocs.org/en/latest/api/core)
