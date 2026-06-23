import discord
from discord import app_commands
from discord.ext import commands

from bot.services.auction_service import AuctionService
from bot.views.auction_view import AuctionLiveView, AuctionSearchView


class AuctionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = AuctionService()

    @commands.command(name="auctions")
    async def list_auctions_prefix(self, ctx: commands.Context):
        auctions = self.service.list_auctions()
        if not auctions:
            return await ctx.reply("No auctions found.")

        lines = [
            f"#{auction.id} | item={auction.item_id} | {auction.status} | {auction.current_price}"
            for auction in auctions[:10]
        ]
        await ctx.reply("\n".join(lines))

    @app_commands.command(name="auctions", description="List auctions")
    async def list_auctions_slash(self, interaction: discord.Interaction):
        auctions = self.service.list_auctions()
        if not auctions:
            return await interaction.response.send_message("No auctions found.", ephemeral=True)

        lines = [
            f"#{auction.id} | item={auction.item_id} | {auction.status} | {auction.current_price}"
            for auction in auctions[:10]
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(name="create_auction", description="Create an auction draft")
    @app_commands.describe(show_id="Show ID", item_id="Item ID")
    async def create_auction(
        self,
        interaction: discord.Interaction,
        show_id: int,
        item_id: int,
    ):
        auction = self.service.create_auction(show_id=show_id, item_id=item_id, status="draft")
        await interaction.response.send_message(
            f"Created auction draft #{auction.id} for item {item_id}.",
            ephemeral=True,
        )

    @app_commands.command(
        name="start_auction",
        description="Start an auction by ID and post live buttons",
    )
    @app_commands.describe(auction_id="Auction ID")
    async def start_auction(self, interaction: discord.Interaction, auction_id: int):
        auction, item, show, error = self.service.start_auction(auction_id)
        if error:
            return await interaction.response.send_message(error, ephemeral=True)

        seller_id = getattr(show, "seller_id", interaction.user.id) if show else interaction.user.id
        view = AuctionLiveView(self.service, auction.id, seller_id)
        view.last_item = item
        view.last_auction = auction
        view.last_show = show

        embed = view.build_embed(auction, item, show)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(name="search_auction", description="Open auction search UI")
    async def search_auction(self, interaction: discord.Interaction):
        view = AuctionSearchView(self.service)
        await interaction.response.send_message(
            "Search an item to start its auction.",
            view=view,
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(AuctionsCog(bot))