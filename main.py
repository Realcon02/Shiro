import asyncio
import signal

from bot import Shiro


# logging.basicConfig(
#     level = logging.INFO, filename="bot.log",
#     format = "%(asctime)s | %(levelname)s | %(message)s"
# )

async def main():
    bot = Shiro()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(
        signal.SIGTERM,
        lambda: loop.create_task(bot.close())
    )

    try:
        await bot.setup()
        await bot.start()
    finally:
        print("Cleaning up resources...")
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully by user")
