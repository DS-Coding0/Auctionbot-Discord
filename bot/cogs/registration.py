import discord
from discord import app_commands
from discord.ext import commands

from bot.repositories.registration_repository import RegistrationRepository


class RegistrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo = RegistrationRepository()

    @commands.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context):
        await ctx.reply(f"Pong! {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Pong! {round(self.bot.latency * 1000)}ms",
            ephemeral=True,
        )

    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_prefix(self, ctx: commands.Context):
        synced = await self.bot.tree.sync()
        await ctx.reply(f"Synced {len(synced)} commands.")

    @app_commands.command(
        name="register",
        description="Register your Discord account in the system",
    )
    async def register(self, interaction: discord.Interaction):
        repo = RegistrationRepository()
        user = interaction.user

        try:
            db_user = await repo.register_discord_user(
                discord_id=str(user.id),
                username=user.name,
                global_name=getattr(user, "global_name", None),
                avatar=str(user.display_avatar.url)
                if getattr(user, "display_avatar", None)
                else None,
            )

            await interaction.response.send_message(
                f"Registered: {db_user.username}",
                ephemeral=True,
            )
        except Exception as error:
            await interaction.response.send_message(
                f"Registration failed: {error}",
                ephemeral=True,
            )
        finally:
            await repo.close()


async def setup(bot):
    await bot.add_cog(RegistrationCog(bot))