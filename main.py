import asyncio
import logging

import discord
from discord import app_commands

from bot.client import BotClient
from bot.config import config
from db.session import init_models


logger = logging.getLogger(__name__)


def setup_logging():
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def setup_app_command_error_handler(bot: BotClient):
    @bot.tree.error
    async def on_app_command_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        logger.exception("Unhandled app command error", exc_info=error)

        if isinstance(error, app_commands.MissingPermissions):
            message = "Du hast keine Berechtigung für diesen Slash-Command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "Mir fehlen die benötigten Berechtigungen für diesen Slash-Command."
        elif isinstance(error, app_commands.CommandOnCooldown):
            message = f"Dieser Slash-Command hat Cooldown. Bitte warte {error.retry_after:.1f}s."
        elif isinstance(error, app_commands.CheckFailure):
            message = "Dieser Slash-Command ist für dich nicht erlaubt."
        elif isinstance(error, app_commands.CommandInvokeError):
            message = "Beim Ausführen des Slash-Commands ist ein interner Fehler aufgetreten."
        else:
            message = "Ein unerwarteter Fehler ist aufgetreten."

        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            logger.warning("Could not send app command error response", exc_info=True)


async def main():
    setup_logging()

    if not config.token:
        raise RuntimeError("DISCORD_TOKEN is missing")
    
    await init_models()

    bot = BotClient()
    setup_app_command_error_handler(bot)

    async with bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())