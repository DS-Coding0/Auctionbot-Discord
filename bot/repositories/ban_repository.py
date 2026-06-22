from db.repository import Repository


class BanRepository(Repository):
    def ban_buyer(self, seller_id: int, buyer_id: int, reason: str | None = None, active: bool = True):
        return self.upsert_ban(seller_id=seller_id, buyer_id=buyer_id, reason=reason, active=active)