from bot.repositories.show_repository import ShowRepository


class ShowService:
    def __init__(self, repo: ShowRepository | None = None):
        self.repo = repo or ShowRepository()

    async def list_shows(self, server_id: int | None = None, seller_id: int | None = None, status: str | None = None):
        return await self.repo.list_shows(server_id=server_id, seller_id=seller_id, status=status)

    async def create_show(
        self,
        server_id: int,
        seller_id: int,
        name: str,
        description: str | None = None,
        status: str = "draft",
        starts_at=None,
        ends_at=None,
        voice_channel_id: int | None = None,
    ):
        return await self.repo.create_show(
            server_id=server_id,
            seller_id=seller_id,
            name=name,
            description=description,
            status=status,
            starts_at=starts_at,
            ends_at=ends_at,
            voice_channel_id=voice_channel_id,
        )

    async def get_show(self, show_id: int):
        return await self.repo.get_show(show_id)

    async def update_show(self, show_id: int, **kwargs):
        return await self.repo.update_show(show_id, **kwargs)

    async def start_show(self, show_id: int, voice_channel_id: int):
        return await self.repo.update_show(
            show_id,
            status="live",
            voice_channel_id=voice_channel_id,
        )

    async def delete_show(self, show_id: int):
        return await self.repo.delete_show(show_id)

    async def close(self):
        await self.repo.close()