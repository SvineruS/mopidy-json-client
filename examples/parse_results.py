import asyncio

from mopidy_async_client import MopidyClient


async def event_handler(event, data):
    print(event, data)


async def main():
    async with MopidyClient(parse_results=True) as mopidy:
        mopidy.listener.bind('*', event_handler)
        res = await mopidy.tracklist.get_tracks()
        print(res)

        await mopidy.playback.next()
        await asyncio.sleep(5)  # wait for event, keep event loop running


asyncio.run(main())
