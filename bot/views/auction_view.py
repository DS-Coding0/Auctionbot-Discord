import discord
from discord import ui
from datetime import datetime, timezone

from bot.config import config
from bot.services.auction_service import AuctionService


class BidModal(ui.Modal, title='Place bid'):
    amount = ui.TextInput(label='Bid amount', placeholder='Enter your bid', required=True)

    def __init__(self, service: AuctionService, auction_id: int, seller_id: int | None):
        super().__init__()
        self.service = service
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.view = None

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = float(self.amount.value)
        except ValueError:
            return await interaction.response.send_message('Invalid amount.', ephemeral=True)
        updated, error = self.service.bid(
            auction_id=self.auction_id,
            buyer_id=interaction.user.id,
            amount=amount,
            min_increment=config.min_bid_increment,
            seller_id=self.seller_id,
        )
        if error:
            return await interaction.response.send_message(error, ephemeral=True)
        if self.view:
            self.view.last_auction = updated
            await self.view.refresh()
        await interaction.response.send_message(f'Bid accepted. New price: {updated.current_price}', ephemeral=True)


class StartAuctionModal(ui.Modal, title='Start auction by item name'):
    item_name = ui.TextInput(label='Item name', placeholder='Search by item name', required=True)

    def __init__(self, service: AuctionService):
        super().__init__()
        self.service = service

    async def on_submit(self, interaction: discord.Interaction):
        auctions = self.service.list_auctions(status='draft')
        needle = self.item_name.value.strip().lower()
        matches = []
        for auction in auctions:
            _, item = self.service.repo.get_auction_with_item(auction.id)
            if item and needle in str(getattr(item, 'title', '')).lower():
                matches.append((auction, item))
        if not matches:
            return await interaction.response.send_message('No matching draft auctions found.', ephemeral=True)
        view = AuctionSearchResultsView(self.service, matches)
        await interaction.response.send_message('Select an auction to start:', view=view, ephemeral=True)


class AuctionSearchResultsView(ui.View):
    def __init__(self, service: AuctionService, matches: list, timeout: float | None = 120):
        super().__init__(timeout=timeout)
        self.service = service
        self.matches = matches[:25]
        if not self.matches:
            return
        options = []
        for auction, item in self.matches:
            label = str(getattr(item, 'title', f'Auction #{auction.id}'))[:100]
            description = f'Auction #{auction.id} | {getattr(auction, "status", "draft")}'[:100]
            options.append(discord.SelectOption(label=label, value=str(auction.id), description=description))
        self.select = ui.Select(placeholder='Choose an auction', options=options)
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
            return await interaction.response.send_message('Auction not found.', ephemeral=True)
        started, item, show, error = self.service.start_auction(selected.id)
        if error:
            return await interaction.response.send_message(error, ephemeral=True)
        seller_id = getattr(show, 'seller_id', interaction.user.id) if show else interaction.user.id
        view = AuctionLiveView(self.service, started.id, seller_id)
        view.last_item = item
        view.last_auction = started
        view.last_show = show
        embed = view.build_embed(started, item, show)
        await interaction.response.send_message(embed=embed, view=view)
        try:
            view.message = await interaction.original_response()
        except Exception:
            view.message = None


class AuctionLiveView(ui.View):
    def __init__(self, service: AuctionService, auction_id: int, seller_id: int | None, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.service = service
        self.auction_id = auction_id
        self.seller_id = seller_id
        self.message = None
        self.last_item = None
        self.last_auction = None
        self.last_show = None

    def build_embed(self, auction, item=None, show=None):
        embed = discord.Embed(title=getattr(item, 'title', f'Auction #{auction.id}'), color=discord.Color.blurple())
        embed.add_field(name='Auction ID', value=str(auction.id), inline=True)
        embed.add_field(name='Current Price', value=str(getattr(auction, 'current_price', '0')), inline=True)
        embed.add_field(name='Status', value=str(getattr(auction, 'status', 'unknown')), inline=True)
        if item is not None:
            embed.add_field(name='Start Price', value=str(getattr(item, 'start_price', '0')), inline=True)
            embed.add_field(name='Min Increment', value=str(getattr(item, 'min_increment', config.min_bid_increment)), inline=True)
            if getattr(item, 'instant_buy_price', None) is not None:
                embed.add_field(name='Instant Buy', value=str(item.instant_buy_price), inline=True)
        ends_at = getattr(auction, 'ends_at', None) or getattr(show, 'ends_at', None)
        if ends_at:
            if isinstance(ends_at, datetime) and ends_at.tzinfo is None:
                ends_at = ends_at.replace(tzinfo=timezone.utc)
            remaining = ends_at - datetime.now(timezone.utc)
            embed.add_field(name='Remaining', value=str(remaining).split('.')[0], inline=True)
        image_url = getattr(item, 'image_url', None) if item else None
        if image_url:
            embed.set_image(url=image_url)
        description = getattr(item, 'description', None)
        if description:
            embed.description = description
        return embed

    async def refresh(self):
        auction, item = self.service.repo.get_auction_with_item(self.auction_id)
        if not auction:
            return
        show = self.service.repo.get_show(auction.show_id)
        self.last_auction = auction
        self.last_item = item
        self.last_show = show
        embed = self.build_embed(auction, item, show)
        if self.message:
            await self.message.edit(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        auction = self.service.get_auction(self.auction_id)
        if not auction or getattr(auction, 'status', None) != 'live':
            await interaction.response.send_message('This auction is not live.', ephemeral=True)
            return False
        if self.seller_id and interaction.user.id == self.seller_id:
            await interaction.response.send_message('Seller cannot bid on own auction.', ephemeral=True)
            return False
        return True

    @ui.button(label='Bid', style=discord.ButtonStyle.primary)
    async def bid_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = BidModal(self.service, self.auction_id, self.seller_id)
        modal.view = self
        await interaction.response.send_modal(modal)

    @ui.button(label='Instant Buy', style=discord.ButtonStyle.success)
    async def instant_buy_button(self, interaction: discord.Interaction, button: ui.Button):
        if not config.instant_buy_enabled:
            return await interaction.response.send_message('Instant buy is disabled.', ephemeral=True)
        result, error = self.service.instant_buy(self.auction_id, interaction.user.id)
        if error:
            return await interaction.response.send_message(error, ephemeral=True)
        if self.message:
            await self.refresh()
        await interaction.response.send_message(f'Instant buy completed. Order #{result["order"].id}', ephemeral=True)


class AuctionSearchView(ui.View):
    def __init__(self, service: AuctionService, timeout: float | None = 120):
        super().__init__(timeout=timeout)
        self.service = service

    @ui.button(label='Search Item', style=discord.ButtonStyle.secondary)
    async def search_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(StartAuctionModal(self.service))