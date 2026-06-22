from bot.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository | None = None):
        self.repo = repo or OrderRepository()

    def list_orders(self, buyer_id: int | None = None, seller_id: int | None = None, status: str | None = None):
        return self.repo.list_orders(buyer_id=buyer_id, seller_id=seller_id, status=status)

    def create_order(self, buyer_id: int, seller_id: int | None, item_id: int, auction_id: int | None = None, quantity: int = 1, total_price: float = 0, status: str = 'pending'):
        return self.repo.create_order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_id=item_id,
            auction_id=auction_id,
            quantity=quantity,
            total_price=total_price,
            status=status,
        )