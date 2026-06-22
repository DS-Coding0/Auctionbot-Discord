from db.repository import Repository


class AuditRepository(Repository):
    def create_log(self, type: str, message: str, entity_type: str | None = None, entity_id: str | None = None):
        return super().create_log(type=type, message=message, entity_type=entity_type, entity_id=entity_id)