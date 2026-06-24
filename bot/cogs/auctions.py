import discord
from discord import app_commands
from discord.ext import commands

from bot.services.auction_service import AuctionService
from bot.views.auction_view import AuctionLiveView, AuctionSearchView


class AuctionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="auctions")
    async def list_auctions_prefix(self, ctx: commands.Context):
        service = AuctionService()
        try:
            auctions = await service.list_auctions()
            if not auctions:
                await ctx.reply("No auctions found.")
                return

            lines = [
                f"#{auction.id} | item={auction.item_id} | {auction.status} | {auction.current_price}"
                for auction in auctions[:10]
            ]
            await ctx.reply("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="auctions", description="List auctions")
    async def list_auctions_slash(self, interaction: discord.Interaction):
        service = AuctionService()
        try:
            await interaction.response.defer(ephemeral=True)

            auctions = await service.list_auctions()
            if not auctions:
                await interaction.followup.send("No auctions found.")
                return

            lines = [
                f"#{auction.id} | item={auction.item_id} | {auction.status} | {auction.current_price}"
                for auction in auctions[:10]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="create_auction", description="Create an auction draft")
    @app_commands.describe(show_id="Show ID", item_id="Item ID")
    async def create_auction(
        self,
        interaction: discord.Interaction,
        show_id: int,
        item_id: int,
    ):
        service = AuctionService()
        try:
            await interaction.response.defer(ephemeral=True)

            auction = await service.create_auction(
                show_id=show_id,
                item_id=item_id,
                status="draft",
            )

            await interaction.followup.send(
                f"Created auction draft #{auction.id} for item {item_id}."
            )
        finally:
            await service.close()

    @app_commands.command(name="start_auction", description="Start an auction")
    @app_commands.describe(
        auction_id="Auction ID",
        duration_seconds="Initial runtime in seconds",
        reset_seconds="Reset-to time in final seconds",
    )
    async def start_auction(
        self,
        interaction: discord.Interaction,
        auction_id: int,
        duration_seconds: int,
        reset_seconds: int,
    ):
        service = AuctionService()
        try:
            await interaction.response.defer()

            if duration_seconds <= 0:
                await interaction.followup.send("duration_seconds must be > 0", ephemeral=True)
                return

            if reset_seconds <= 0:
                await interaction.followup.send("reset_seconds must be > 0", ephemeral=True)
                return

            if reset_seconds > duration_seconds:
                await interaction.followup.send(
                    "reset_seconds cannot be greater than duration_seconds.",
                    ephemeral=True,
                )
                return

            auction, item, show, error = await service.start_auction(
                auction_id=auction_id,
                duration_seconds=duration_seconds,
                reset_seconds=reset_seconds,
            )

            if error:
                await interaction.followup.send(error, ephemeral=True)
                return

            seller_id = getattr(show, "seller_id", None) if show else None

            view = AuctionLiveView(
                service=service,
                auction_id=auction.id,
                seller_id=seller_id,
            )
            view.last_item = item
            view.last_auction = auction
            view.last_show = show

            embed = view.build_embed(auction, item, show)
            message = await interaction.followup.send(
                embed=embed,
                view=view,
                wait=True,
            )
            view.message = message
            view.start_countdown()
            service = None
        finally:
            if service is not None:
                await service.close()

    @app_commands.command(name="search_auction", description="Open auction search UI")
    async def search_auction(self, interaction: discord.Interaction):
        view = AuctionSearchView()
        await interaction.response.send_message(
            "Search an item to start its auction.",
            view=view,
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(AuctionsCog(bot))