# Mopidy-Async-Client 

### Fork of [Mopidy-json-client](https://github.com/ismailof/mopidy-json-client), but from scratch and async


Async Mopidy Client via JSON/RPC Websocket interface

## Usage

mopidy-async-client provides a main class `MopidyClient`, which manages the connection and methods to the Mopidy Server.

```python
import asyncio

from mopidy_async_client import MopidyClient


async def playback_started_handler(**data):
    print(data)


async def all_events_handler(event, **data):
    print(event, data)


async def main1():
    async with MopidyClient() as mopidy:  # close connection explicit
        await mopidy.playback.play()


async def main2():
    mopidy = await MopidyClient().connect()
    mopidy.listener.bind('track_playback_started', playback_started_handler)
    mopidy.listener.bind('*', all_events_handler)

    # your app logic
    for i in range(10):
        await asyncio.sleep(5)
    # end your app logic

    await mopidy.disconnect()  # close connection implicit


asyncio.run(main1())
# or 
asyncio.run(main2())

```

## Installation

 `pip install mopidy-async-client`


## References
- [Mopidy Core API](https://mopidy.readthedocs.org/en/latest/api/core)
