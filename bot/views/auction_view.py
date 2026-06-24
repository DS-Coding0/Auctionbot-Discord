from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import discord
from discord import ui

from bot.config import config
from bot.services.auction_service import AuctionService
from bot.services.user_service import UserService


class BidModal(ui.Modal, title="Place bid"):
    amount = ui.TextInput(
        label="Bid amount",
        placeholder="Enter your bid",
        required=True,
    )

    def __init__(self, auction_id: int, seller_id: int | None):
        super().__init__()
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.auction_view: AuctionLiveView | None = None

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = float(self.amount.value)
        except ValueError:
            await interaction.response.send_message("Invalid amount.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message(
                "Bid amount must be greater than 0.",
                ephemeral=True,
            )
            return

        service = AuctionService()
        users = UserService()
        try:
            buyer_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="buyer",
            )

            updated, error = await service.bid(
                auction_id=self.auction_id,
                buyer_id=buyer_db_user.id,
                amount=amount,
                min_increment=config.min_bid_increment,
                seller_id=self.seller_id,
            )

            if error:
                await interaction.response.send_message(error, ephemeral=True)
                return

            if self.auction_view:
                self.auction_view.last_auction = updated
                await self.auction_view.refresh()

            await interaction.response.send_message(
                f"Bid accepted. New price: {updated.current_price}",
                ephemeral=True,
            )
        finally:
            await service.close()
            await users.close()


class StartAuctionModal(ui.Modal, title="Start auction by item name"):
    item_name = ui.TextInput(
        label="Item name",
        placeholder="Search by item name",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        needle = self.item_name.value.strip().lower()

        service = AuctionService()
        try:
            auctions = await service.list_auctions(status="draft")
            matches: list[tuple[object, object]] = []

            for auction in auctions:
                current_auction, item = await service.repo.get_auction_with_item(auction.id)
                if item and needle in str(getattr(item, "title", "")).lower():
                    matches.append((current_auction, item))

            if not matches:
                await interaction.response.send_message(
                    "No matching draft auctions found.",
                    ephemeral=True,
                )
                return

            view = AuctionSearchResultsView(matches)
            await interaction.response.send_message(
                "Select an auction to start:",
                view=view,
                ephemeral=True,
            )
        finally:
            await service.close()


class AuctionSearchResultsView(ui.View):
    def __init__(self, matches: list[tuple[object, object]], timeout: float | None = 120):
        super().__init__(timeout=timeout)
        self.matches = matches[:25]

        if not self.matches:
            return

        options = []
        for auction, item in self.matches:
            label = str(getattr(item, "title", f"Auction #{auction.id}"))[:100]
            description = f'Auction #{auction.id} | {getattr(auction, "status", "draft")}'[:100]
            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(auction.id),
                    description=description,
                )
            )

        self.select = ui.Select(
            placeholder="Choose an auction",
            options=options,
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        auction_id = int(self.select.values[0])

        selected = None
        item = None
        for auction, itm in self.matches:
            if auction.id == auction_id:
                selected = auction
                item = itm
                break

        if selected is None:
            await interaction.response.send_message("Auction not found.", ephemeral=True)
            return

        service = AuctionService()
        try:
            started, item, show, error = await service.start_auction(selected.id)
            if error:
                await interaction.response.send_message(error, ephemeral=True)
                return

            seller_id = getattr(show, "seller_id", None) if show else None

            view = AuctionLiveView(
                auction_id=started.id,
                seller_id=seller_id,
            )
            view.last_item = item
            view.last_auction = started
            view.last_show = show

            embed = view.build_embed(started, item, show)
            await interaction.response.send_message(embed=embed, view=view)

            try:
                view.message = await interaction.original_response()
            except Exception:
                view.message = None
        finally:
            await service.close()


class AuctionLiveView(ui.View):
    def __init__(
        self,
        auction_id: int,
        seller_id: int | None,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.message: discord.Message | None = None
        self.last_item = None
        self.last_auction = None
        self.last_show = None

    def build_embed(self, auction, item=None, show=None):
        embed = discord.Embed(
            title=getattr(item, "title", f"Auction #{auction.id}"),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Auction ID", value=str(auction.id), inline=True)
        embed.add_field(
            name="Current Price",
            value=str(getattr(auction, "current_price", "0")),
            inline=True,
        )
        embed.add_field(
            name="Status",
            value=str(getattr(auction, "status", "unknown")),
            inline=True,
        )

        if item is not None:
            embed.add_field(
                name="Start Price",
                value=str(getattr(item, "start_price", "0")),
                inline=True,
            )
            embed.add_field(
                name="Min Increment",
                value=str(getattr(item, "min_increment", config.min_bid_increment)),
                inline=True,
            )
            if getattr(item, "instant_buy_price", None) is not None:
                embed.add_field(
                    name="Instant Buy",
                    value=str(item.instant_buy_price),
                    inline=True,
                )

        ends_at = getattr(auction, "ends_at", None) or getattr(show, "ends_at", None)
        if ends_at:
            if isinstance(ends_at, datetime) and ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=ZoneInfo("Europe/Berlin"))
            remaining = ends_at - datetime.now(ZoneInfo("Europe/Berlin"))
            embed.add_field(
                name="Remaining",
                value=str(remaining).split(".")[0],
                inline=True,
            )

        image_url = getattr(item, "image_url", None) if item else None
        if image_url:
            embed.set_image(url=image_url)

        description = getattr(item, "description", None)
        if description:
            embed.description = description

        return embed

    async def refresh(self):
        service = AuctionService()
        try:
            auction, item = await service.repo.get_auction_with_item(self.auction_id)
            if not auction:
                return

            show = await service.repo.get_show(auction.show_id)

            self.last_auction = auction
            self.last_item = item
            self.last_show = show

            embed = self.build_embed(auction, item, show)
            if self.message:
                await self.message.edit(embed=embed, view=self)
        finally:
            await service.close()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        service = AuctionService()
        users = UserService()
        try:
            auction = await service.get_auction(self.auction_id)
            if not auction or getattr(auction, "status", None) != "live":
                await interaction.response.send_message(
                    "This auction is not live.",
                    ephemeral=True,
                )
                return False

            buyer_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="buyer",
            )

            if self.seller_id and buyer_db_user.id == self.seller_id:
                await interaction.response.send_message(
                    "Seller cannot bid on own auction.",
                    ephemeral=True,
                )
                return False

            return True
        finally:
            await service.close()
            await users.close()

    @ui.button(label="Bid", style=discord.ButtonStyle.primary)
    async def bid_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = BidModal(
            auction_id=self.auction_id,
            seller_id=self.seller_id,
        )
        modal.auction_view = self
        await interaction.response.send_modal(modal)

    @ui.button(label="Instant Buy", style=discord.ButtonStyle.success)
    async def instant_buy_button(self, interaction: discord.Interaction, button: ui.Button):
        service = AuctionService()
        users = UserService()
        try:
            if not config.instant_buy_enabled:
                await interaction.response.send_message(
                    "Instant buy is disabled.",
                    ephemeral=True,
                )
                return

            buyer_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="buyer",
            )

            result, error = await service.instant_buy(
                self.auction_id,
                buyer_db_user.id,
            )
            if error:
                await interaction.response.send_message(error, ephemeral=True)
                return

            if self.message:
                await self.refresh()

            await interaction.response.send_message(
                f'Instant buy completed. Order #{result["order"].id}',
                ephemeral=True,
            )
        finally:
            await service.close()
            await users.close()


class AuctionSearchView(ui.View):
    def __init__(self, timeout: float | None = 120):
        super().__init__(timeout=timeout)

    @ui.button(label="Search Item", style=discord.ButtonStyle.secondary)
    async def search_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(StartAuctionModal())