from db.repository import Repository


class AuctionRepository(Repository):
    def get_auction_with_item(self, auction_id: int):
        auction = self.get_auction(auction_id)
        if not auction:
            return None, None

        item = self.get_item(auction.item_id)
        return auction, item

    def list_live_auctions(self):
        return self.list_auctions(status="live")

    def update_price(self, auction_id: int, price: float, status: str | None = None):
        data = {"current_price": price}
        if status is not None:
            data["status"] = status
        return self.update_auction(auction_id, **data)