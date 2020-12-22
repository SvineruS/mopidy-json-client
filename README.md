# Mopidy-Async-Client 

### Fork of [Mopidy-json-client](https://github.com/ismailof/mopidy-json-client), but from scratch and async


Async Mopidy Client via JSON/RPC Websocket interface

## Usage

mopidy-async-client provides a main class `MopidyClient`, which manages the connection and methods to the Mopidy Server.

```python
import asyncio

from mopidy_async_client import MopidyClient


async def playback_started_handler(data):
    print(data)


async def all_events_handler(event, data):
    print(event, data)


async def main1():
    async with MopidyClient(url='ws://some_ip:6680/mopidy/ws') as mopidy:  # close connection explicit
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

### Parse results

You can specify `parse_results=True` in `MopidyClient` and get Mopidy objects instead of json dictionaries.
To do this, you need to install Mopidy locally (only for importing models)

```python
async with MopidyClient(parse_results=True) as mopidy:
    res = await mopidy.tracklist.get_tracks()
    print(res)

>>> [Track(date='2020-01-01', length=392533, name='audio.mp3', uri='file:///home/svin/Music/audio.mp3')]
# instead of
>>> [{'__model__': 'Track', 'uri': 'file:///home/svin/Music/audio.mp3', 'name': 'audio.mp3', 'date': '2020-01-01', 'length': 392533}]
```



## Installation

 `pip install mopidy-async-client`


## References
- [Mopidy Core API](https://mopidy.readthedocs.org/en/latest/api/core)
