from bot.services.audit_service import AuditService


class RecoveryService:
    def __init__(self, repo=None):
        self.audit = AuditService()
        self.repo = repo

    async def recover(self):
        self.audit.log(type='recovery', message='Recovery started')