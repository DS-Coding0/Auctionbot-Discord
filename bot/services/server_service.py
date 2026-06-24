from bot.repositories.server_repository import ServerRepository


class ServerService:
    def __init__(self, repo: ServerRepository | None = None):
        self.repo = repo or ServerRepository()

    async def get_server(self, server_id: int):
        return self.repo.get_server(server_id)

    async def get_or_create_server(self, guild):
        return self.repo.get_or_create_server(
            server_id=guild.id,
            name=guild.name,
        )

    async def close(self):
        self.repo.close()