import discord
from discord import app_commands
from discord.ext import commands

from bot.services.item_service import ItemService


class ItemsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="items", description="List items in a show")
    @app_commands.describe(show_id="Show ID")
    async def list_items(
        self,
        interaction: discord.Interaction,
        show_id: int | None = None,
    ):
        service = ItemService()
        try:
            await interaction.response.defer(ephemeral=True)
            items = await service.list_items(show_id=show_id)

            if not items:
                await interaction.followup.send("No items found.")
                return

            lines = [
                f"#{item.id} | {item.title} | {item.status} | start={item.start_price}"
                for item in items[:10]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="create_item", description="Create an item in a show")
    @app_commands.describe(
        show_id="Show ID",
        title="Item title",
        description="Optional description",
        image_url="Optional image URL",
        start_price="Starting price",
        instant_buy_price="Optional instant buy price",
        min_increment="Minimum bid increment",
        status="Initial item status",
    )
    async def create_item(
        self,
        interaction: discord.Interaction,
        show_id: int,
        title: str,
        description: str | None = None,
        image_url: str | None = None,
        start_price: float = 0.0,
        instant_buy_price: float | None = None,
        min_increment: float = 1.0,
        status: str = "draft",
    ):
        service = ItemService()
        try:
            await interaction.response.defer(ephemeral=True)

            item = await service.create_item(
                show_id=show_id,
                title=title,
                description=description,
                image_url=image_url,
                start_price=start_price,
                instant_buy_price=instant_buy_price,
                min_increment=min_increment,
                status=status,
            )

            await interaction.followup.send(f"Created item #{item.id}: {item.title}")
        finally:
            await service.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(ItemsCog(bot))