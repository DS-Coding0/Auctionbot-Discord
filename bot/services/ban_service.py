from bot.repositories.ban_repository import BanRepository


class BanService:
    def __init__(self, repo: BanRepository | None = None):
        self.repo = repo or BanRepository()

    def is_buyer_banned(self, seller_id: int, buyer_id: int) -> bool:
        return self.repo.is_buyer_banned(seller_id, buyer_id)

    def ban_buyer(self, seller_id: int, buyer_id: int, reason: str | None = None, active: bool = True):
        return self.repo.ban_buyer(seller_id=seller_id, buyer_id=buyer_id, reason=reason, active=active)

    def list_bans(self, seller_id: int | None = None, active: bool | None = None):
        return self.repo.list_bans(seller_id=seller_id, active=active)