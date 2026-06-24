from bot.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, repo: ItemRepository | None = None):
        self.repo = repo or ItemRepository()

    async def list_items(self, show_id: int | None = None, status: str | None = None):
        return await self.repo.list_items(show_id=show_id, status=status)

    async def get_item(self, item_id: int):
        return await self.repo.get_item(item_id)

    async def create_item(
        self,
        show_id: int,
        title: str,
        description: str | None = None,
        image_url: str | None = None,
        start_price: float = 0,
        instant_buy_price: float | None = None,
        min_increment: float = 1,
        status: str = "draft",
    ):
        return await self.repo.create_item(
            show_id=show_id,
            title=title,
            description=description,
            image_url=image_url,
            start_price=start_price,
            instant_buy_price=instant_buy_price,
            min_increment=min_increment,
            status=status,
        )

    async def update_item(self, item_id: int, **kwargs):
        return await self.repo.update_item(item_id, **kwargs)

    async def delete_item(self, item_id: int) -> bool:
        return await self.repo.delete_item(item_id)

    async def close(self):
        await self.repo.close()