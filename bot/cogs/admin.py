from discord import app_commands
from discord.ext import commands

from bot.services.audit_service import AuditService
from bot.services.ban_service import BanService


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audit = AuditService()
        self.bans = BanService()

    @commands.command(name='audit_log')
    @commands.is_owner()
    async def audit_log_prefix(self, ctx: commands.Context, type: str, message: str):
        log = self.audit.log(type=type, message=message)
        await ctx.reply(f'Logged audit entry #{log.id}.')

    @app_commands.command(name='audit_log', description='Create an audit log entry')
    @commands.is_owner()
    async def audit_log_slash(self, interaction, type: str, message: str):
        log = self.audit.log(type=type, message=message)
        await interaction.response.send_message(f'Logged audit entry #{log.id}.', ephemeral=True)

    @app_commands.command(name='ban_buyer', description='Ban a buyer for your own shows')
    @app_commands.describe(buyer_id='Buyer user ID', reason='Optional reason')
    async def ban_buyer(self, interaction, buyer_id: int, reason: str | None = None):
        ban = self.bans.ban_buyer(seller_id=interaction.user.id, buyer_id=buyer_id, reason=reason, active=True)
        await interaction.response.send_message(f'Buyer banned: #{ban.id}', ephemeral=True)

    @app_commands.command(name='unban_buyer', description='Unban a buyer for your own shows')
    @app_commands.describe(buyer_id='Buyer user ID')
    async def unban_buyer(self, interaction, buyer_id: int):
        ban = self.bans.ban_buyer(seller_id=interaction.user.id, buyer_id=buyer_id, reason=None, active=False)
        await interaction.response.send_message(f'Buyer unbanned: #{ban.id}', ephemeral=True)


async def setup(bot):
    cog = AdminCog(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.audit_log_slash)
    bot.tree.add_command(cog.ban_buyer)
    bot.tree.add_command(cog.unban_buyer)