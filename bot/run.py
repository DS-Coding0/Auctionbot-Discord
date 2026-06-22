from bot.client import BotClient
from bot.config import config


def run():
    bot = BotClient(command_prefix=config.command_prefix)
    bot.run(config.token)


if __name__ == '__main__':
    run()