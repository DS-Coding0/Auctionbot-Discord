import discord
from discord import app_commands
from discord.ext import commands

from bot.services.order_service import OrderService


class OrdersCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="orders")
    async def list_orders_prefix(self, ctx: commands.Context):
        service = OrderService()
        try:
            orders = await service.list_orders()
            if not orders:
                await ctx.reply("No orders found.")
                return

            lines = [
                f"#{order.id} | item={order.item_id} | {order.status} | {order.total_price}"
                for order in orders[:10]
            ]
            await ctx.reply("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="orders", description="List orders")
    async def list_orders_slash(self, interaction: discord.Interaction):
        service = OrderService()
        try:
            await interaction.response.defer(ephemeral=True)
            orders = await service.list_orders()

            if not orders:
                await interaction.followup.send("No orders found.")
                return

            lines = [
                f"#{order.id} | item={order.item_id} | {order.status} | {order.total_price}"
                for order in orders[:10]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await service.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(OrdersCog(bot))