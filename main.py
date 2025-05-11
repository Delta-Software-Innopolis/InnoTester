import asyncio
import InnoTester


async def main():
    await InnoTester.start()


if __name__ == "__main__":
    asyncio.run(main())
