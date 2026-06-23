from bot.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repo: AuditRepository | None = None):
        self.repo = repo or AuditRepository()

    async def log(
        self,
        type: str,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ):
        return await self.repo.create_log(
            type=type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )

    async def close(self):
        await self.repo.close()