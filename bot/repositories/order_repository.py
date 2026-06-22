from db.repository import Repository


class OrderRepository(Repository):
    def create_order(self, buyer_id: int, seller_id: int | None, item_id: int, auction_id: int | None = None, quantity: int = 1, total_price: float = 0, status: str = 'pending'):
        return super().create_order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_id=item_id,
            auction_id=auction_id,
            quantity=quantity,
            total_price=total_price,
            status=status,
        )