from db.repository import Repository


class BanRepository(Repository):
    async def ban_buyer(
        self,
        seller_id: int,
        buyer_id: int,
        reason: str | None = None,
        active: bool = True,
    ):
        return await self.upsert_ban(
            seller_id=seller_id,
            buyer_id=buyer_id,
            reason=reason,
            active=active,
        )