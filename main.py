import asyncio
import ITPHelper


async def main():
    await ITPHelper.start()


if __name__ == "__main__":
    asyncio.run(main())
