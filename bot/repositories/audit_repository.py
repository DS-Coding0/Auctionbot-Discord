from db.repository import Repository


class AuditRepository(Repository):
    async def create_log(self, **kwargs):
        return await super().create_log(**kwargs)