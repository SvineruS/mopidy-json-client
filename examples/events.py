import asyncio

from mopidy_async_client import MopidyClient


async def playback_started_handler(data):
    print(data)


async def all_events_handler(event, data):
    print(event, data)


async def main():
    mopidy = await MopidyClient().connect()
    mopidy.listener.bind('track_playback_started', playback_started_handler)
    mopidy.listener.bind('*', all_events_handler)

    # your app logic
    for i in range(10):
        await asyncio.sleep(5)
    # end your app logic

    await mopidy.disconnect()  # close connection implicit


asyncio.run(main())
