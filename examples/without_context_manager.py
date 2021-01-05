import asyncio

from mopidy_async_client import MopidyClient


async def main():
    mopidy = await MopidyClient().connect()

    # your app logic
    for i in range(10):
        await asyncio.sleep(5)
    # end your app logic

    await mopidy.disconnect()  # close connection implicit


asyncio.run(main())
