import asyncio

from mopidy_async_client import MopidyClient


async def main():
    async with MopidyClient() as mopidy:  # close connection explicit
        await mopidy.playback.play()


asyncio.run(main())
