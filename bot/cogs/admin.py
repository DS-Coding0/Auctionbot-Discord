import discord
from discord import app_commands
from discord.ext import commands

from bot.services.audit_service import AuditService
from bot.services.ban_service import BanService
from bot.services.user_service import UserService


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="audit_log")
    @commands.is_owner()
    async def audit_log_prefix(
        self,
        ctx: commands.Context,
        type: str,
        *,
        message: str,
    ):
        audit = AuditService()
        try:
            log = await audit.log(type=type, message=message)
            await ctx.reply(f"Logged audit entry #{log.id}.")
        finally:
            await audit.close()

    @app_commands.command(name="audit_log", description="Create an audit log entry")
    async def audit_log_slash(
        self,
        interaction: discord.Interaction,
        type: str,
        message: str,
    ):
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(
                "You are not allowed to use this command.",
                ephemeral=True,
            )
            return

        audit = AuditService()
        try:
            await interaction.response.defer(ephemeral=True)
            log = await audit.log(type=type, message=message)
            await interaction.followup.send(f"Logged audit entry #{log.id}.")
        finally:
            await audit.close()

    @app_commands.command(name="ban_buyer", description="Ban a buyer for your own auctions")
    @app_commands.describe(buyer="Buyer to ban", reason="Optional reason")
    @app_commands.guild_only()
    async def ban_buyer(
        self,
        interaction: discord.Interaction,
        buyer: discord.User,
        reason: str | None = None,
    ):
        bans = BanService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            if interaction.user.id == buyer.id:
                await interaction.followup.send("You cannot ban yourself.")
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )
            buyer_db_user = await users.get_or_create_from_discord_user(
                buyer,
                role="buyer",
            )

            ban = await bans.ban_buyer(
                seller_id=seller_db_user.id,
                buyer_id=buyer_db_user.id,
                reason=reason,
                active=True,
            )
            await interaction.followup.send(f"Buyer banned: #{ban.id}")
        finally:
            await bans.close()
            await users.close()

    @app_commands.command(name="unban_buyer", description="Unban a buyer for your own auctions")
    @app_commands.describe(buyer="Buyer to unban")
    @app_commands.guild_only()
    async def unban_buyer(
        self,
        interaction: discord.Interaction,
        buyer: discord.User,
    ):
        bans = BanService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )
            buyer_db_user = await users.get_or_create_from_discord_user(
                buyer,
                role="buyer",
            )

            ban = await bans.ban_buyer(
                seller_id=seller_db_user.id,
                buyer_id=buyer_db_user.id,
                reason=None,
                active=False,
            )
            await interaction.followup.send(f"Buyer unbanned: #{ban.id}")
        finally:
            await bans.close()
            await users.close()

    @app_commands.command(name="my_bans", description="List buyers you have banned")
    @app_commands.describe(active="Filter by active state")
    @app_commands.guild_only()
    async def my_bans(
        self,
        interaction: discord.Interaction,
        active: bool | None = True,
    ):
        bans = BanService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            entries = await bans.list_bans(
                seller_id=seller_db_user.id,
                active=active,
            )

            if not entries:
                await interaction.followup.send("No bans found.")
                return

            lines = [
                f"#{entry.id} | buyer_db={entry.buyer_id} | active={entry.active}"
                for entry in entries[:20]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await bans.close()
            await users.close()

    @app_commands.command(name="admin_bans", description="List bans for a seller")
    @app_commands.describe(
        seller="Seller user",
        active="Filter by active state",
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def admin_bans(
        self,
        interaction: discord.Interaction,
        seller: discord.User,
        active: bool | None = None,
    ):
        bans = BanService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            seller_db_user = await users.get_or_create_from_discord_user(
                seller,
                role="seller",
            )

            entries = await bans.list_bans(
                seller_id=seller_db_user.id,
                active=active,
            )

            if not entries:
                await interaction.followup.send("No bans found.")
                return

            lines = [
                f"#{entry.id} | seller_db={entry.seller_id} | buyer_db={entry.buyer_id} | active={entry.active}"
                for entry in entries[:20]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await bans.close()
            await users.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))