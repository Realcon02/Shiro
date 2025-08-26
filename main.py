import asyncio
from bot import Shiro

# logging.basicConfig(
#     level = logging.INFO, filename="bot.log",
#     format = "%(asctime)s | %(levelname)s | %(message)s"
# )

async def main():
    bot = Shiro()
    try:
        await bot.setup()
        await bot.start()
    finally:
        print("Cleaning up resources...")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully by user")
