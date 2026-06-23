from db.repository import Repository


class AuditRepository(Repository):
    async def create_audit_log(
        self,
        type: str,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ):
        return await self.repo.create_audit_log(
            type=type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )