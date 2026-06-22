from discord import app_commands
from discord.ext import commands

from bot.services.order_service import OrderService


class OrdersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = OrderService()

    @commands.command(name='orders')
    async def list_orders_prefix(self, ctx: commands.Context):
        orders = self.service.list_orders()
        if not orders:
            return await ctx.reply('No orders found.')
        lines = [f'#{order.id} | item={order.item_id} | {order.status} | {order.total_price}' for order in orders[:10]]
        await ctx.reply('\n'.join(lines))

    @app_commands.command(name='orders', description='List orders')
    async def list_orders_slash(self, interaction):
        orders = self.service.list_orders()
        if not orders:
            return await interaction.response.send_message('No orders found.', ephemeral=True)
        lines = [f'#{order.id} | item={order.item_id} | {order.status} | {order.total_price}' for order in orders[:10]]
        await interaction.response.send_message('\n'.join(lines), ephemeral=True)

    @app_commands.command(name='create_order', description='Create an order manually')
    @app_commands.describe(buyer_id='Buyer user ID', item_id='Item ID', total_price='Total price')
    async def create_order(self, interaction, buyer_id: int, item_id: int, total_price: float, seller_id: int | None = None, auction_id: int | None = None, quantity: int = 1):
        order = self.service.create_order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_id=item_id,
            auction_id=auction_id,
            quantity=quantity,
            total_price=total_price,
        )
        await interaction.response.send_message(f'Created order #{order.id}.', ephemeral=True)


async def setup(bot):
    cog = OrdersCog(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.list_orders_slash)
    bot.tree.add_command(cog.create_order)