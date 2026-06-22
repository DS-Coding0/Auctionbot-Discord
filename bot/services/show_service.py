from bot.repositories.show_repository import ShowRepository


class ShowService:
    def __init__(self, repo: ShowRepository | None = None):
        self.repo = repo or ShowRepository()

    def create_show(self, server_id: int, seller_id: int, name: str, description: str | None = None):
        return self.repo.create_show(server_id=server_id, seller_id=seller_id, name=name, description=description)

    def list_shows(self, server_id: int | None = None, seller_id: int | None = None, status: str | None = None):
        return self.repo.list_shows(server_id=server_id, seller_id=seller_id, status=status)