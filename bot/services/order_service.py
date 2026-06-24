from bot.repositories.order_repository import OrderRepository


class OrderService:
    def __init__(self, repo: OrderRepository | None = None):
        self.repo = repo or OrderRepository()

    async def list_orders(
        self,
        buyer_id: int | None = None,
        seller_id: int | None = None,
        status: str | None = None,
    ):
        return await self.repo.list_orders(
            buyer_id=buyer_id,
            seller_id=seller_id,
            status=status,
        )

    async def create_order(
        self,
        buyer_id: int,
        seller_id: int | None,
        item_id: int,
        auction_id: int | None = None,
        quantity: int = 1,
        total_price: float = 0,
        status: str = "pending",
    ):
        return await self.repo.create_order(
            buyer_id=buyer_id,
            seller_id=seller_id,
            item_id=item_id,
            auction_id=auction_id,
            quantity=quantity,
            total_price=total_price,
            status=status,
        )

    async def get_order(self, order_id: int):
        return await self.repo.get_order(order_id)

    async def update_order(self, order_id: int, **kwargs):
        return await self.repo.update_order(order_id, **kwargs)

    async def delete_order(self, order_id: int) -> bool:
        return await self.repo.delete_order(order_id)

    async def close(self):
        await self.repo.close()