from bot import Shiro

# logging.basicConfig(
#     level = logging.INFO, filename="bot.log",
#     format = "%(asctime)s | %(levelname)s | %(message)s"
# )

if __name__ == "__main__":
    bot = Shiro()
    bot.setup()
    bot.run()
