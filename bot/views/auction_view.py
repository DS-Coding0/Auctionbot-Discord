from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import ui
from discord.ext import tasks

from bot.config import config
from bot.services.auction_service import AuctionService
from bot.services.user_service import UserService


def _now_berlin() -> datetime:
    return datetime.now(ZoneInfo("Europe/Berlin"))


def _to_berlin(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Europe/Berlin"))
    return dt.astimezone(ZoneInfo("Europe/Berlin"))


def _format_remaining(ends_at: datetime | None) -> str:
    if ends_at is None:
        return "—"

    end_local = _to_berlin(ends_at)
    now_local = _now_berlin()
    remaining = end_local - now_local
    total_seconds = max(0, int(remaining.total_seconds()))

    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


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

    duration_seconds = ui.TextInput(
        label="Duration in seconds",
        placeholder="e.g. 60",
        required=True,
    )

    reset_seconds = ui.TextInput(
        label="Reset seconds",
        placeholder="e.g. 10",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        needle = self.item_name.value.strip().lower()

        try:
            duration_seconds = int(self.duration_seconds.value)
            reset_seconds = int(self.reset_seconds.value)
        except ValueError:
            await interaction.response.send_message(
                "Duration and reset seconds must be integers.",
                ephemeral=True,
            )
            return

        if duration_seconds <= 0:
            await interaction.response.send_message(
                "duration_seconds must be > 0",
                ephemeral=True,
            )
            return

        if reset_seconds <= 0:
            await interaction.response.send_message(
                "reset_seconds must be > 0",
                ephemeral=True,
            )
            return

        if reset_seconds > duration_seconds:
            await interaction.response.send_message(
                "reset_seconds cannot be greater than duration_seconds.",
                ephemeral=True,
            )
            return

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

            view = AuctionSearchResultsView(
                matches=matches,
                duration_seconds=duration_seconds,
                reset_seconds=reset_seconds,
            )
            await interaction.response.send_message(
                "Select an auction to start:",
                view=view,
                ephemeral=True,
            )
        finally:
            await service.close()


class AuctionSearchResultsView(ui.View):
    def __init__(
        self,
        matches: list[tuple[object, object]],
        duration_seconds: int,
        reset_seconds: int,
        timeout: float | None = 120,
    ):
        super().__init__(timeout=timeout)
        self.matches = matches[:25]
        self.duration_seconds = duration_seconds
        self.reset_seconds = reset_seconds

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
            started, item, show, error = await service.start_auction(
                auction_id=selected.id,
                duration_seconds=self.duration_seconds,
                reset_seconds=self.reset_seconds,
            )
            if error:
                await interaction.response.send_message(error, ephemeral=True)
                return

            seller_id = getattr(show, "seller_id", None) if show else None

            view = AuctionLiveView(
                service=service,
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
                view.start_countdown()
            except Exception:
                view.message = None

            service = None
        finally:
            if service is not None:
                await service.close()


class AuctionLiveView(ui.View):
    def __init__(
        self,
        service: AuctionService,
        auction_id: int,
        seller_id: int | None,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.service = service
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.message: discord.Message | None = None
        self.last_item = None
        self.last_auction = None
        self.last_show = None
        self._countdown_started = False

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
        reset_seconds = int(getattr(auction, "reset_seconds", 0) or 0)

        if ends_at:
            end_local = _to_berlin(ends_at)
            embed.add_field(
                name="Ends At",
                value=end_local.strftime("%d.%m.%Y %H:%M:%S %Z"),
                inline=False,
            )
            embed.add_field(
                name="Remaining",
                value=_format_remaining(ends_at),
                inline=True,
            )

        if reset_seconds > 0:
            embed.add_field(
                name="Reset Window",
                value=f"{reset_seconds} seconds",
                inline=True,
            )

        highest_bidder_id = getattr(auction, "highest_bidder_id", None)
        if highest_bidder_id is not None:
            embed.add_field(
                name="Highest Bidder",
                value=str(highest_bidder_id),
                inline=True,
            )

        image_url = getattr(item, "image_url", None) if item else None
        if image_url:
            embed.set_image(url=image_url)

        description = getattr(item, "description", None)
        if description:
            embed.description = description

        return embed

    def _disable_buttons(self):
        for child in self.children:
            if isinstance(child, ui.Button):
                child.disabled = True

    async def refresh(self):
        try:
            auction, item = await self.service.repo.get_auction_with_item(self.auction_id)
            if not auction:
                return

            show = await self.service.repo.get_show(auction.show_id)

            self.last_auction = auction
            self.last_item = item
            self.last_show = show

            if getattr(auction, "status", None) != "live":
                self._disable_buttons()

            embed = self.build_embed(auction, item, show)
            if self.message:
                await self.message.edit(embed=embed, view=self)
        except discord.HTTPException:
            return

    def start_countdown(self):
        if not self._countdown_started:
            self._countdown_started = True
            self.countdown_loop.start()

    def stop_countdown(self):
        if self.countdown_loop.is_running():
            self.countdown_loop.cancel()
        self._countdown_started = False

    @tasks.loop(seconds=2.0)
    async def countdown_loop(self):
        if not self.message:
            return

        try:
            auction, item = await self.service.repo.get_auction_with_item(self.auction_id)
            if not auction:
                self.stop_countdown()
                return

            show = await self.service.repo.get_show(auction.show_id)

            self.last_auction = auction
            self.last_item = item
            self.last_show = show

            if getattr(auction, "status", None) != "live":
                self._disable_buttons()
                embed = self.build_embed(auction, item, show)
                await self.message.edit(embed=embed, view=self)
                self.stop_countdown()
                return

            ends_at = getattr(auction, "ends_at", None) or getattr(show, "ends_at", None)
            if ends_at is not None:
                end_local = _to_berlin(ends_at)
                if end_local <= _now_berlin():
                    ended = await self.service.end_auction(self.auction_id)
                    self.last_auction = ended
                    self._disable_buttons()
                    embed = self.build_embed(ended, item, show)
                    await self.message.edit(embed=embed, view=self)
                    self.stop_countdown()
                    return

            embed = self.build_embed(auction, item, show)
            await self.message.edit(embed=embed, view=self)
        except discord.HTTPException:
            self.stop_countdown()

    async def on_timeout(self):
        self._disable_buttons()
        self.stop_countdown()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        users = UserService()
        try:
            auction = await self.service.get_auction(self.auction_id)
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

            result, error = await self.service.instant_buy(
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
            await users.close()


class AuctionSearchView(ui.View):
    def __init__(self, timeout: float | None = 120):
        super().__init__(timeout=timeout)

    @ui.button(label="Search Item", style=discord.ButtonStyle.secondary)
    async def search_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(StartAuctionModal())