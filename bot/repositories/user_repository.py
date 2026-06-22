from db.repository import Repository


class UserRepository(Repository):
    def get_or_create_from_discord(self, discord_id: str, username: str, global_name: str | None = None, avatar: str | None = None, role: str = 'buyer'):
        return self.get_or_create_user(
            discord_id=discord_id,
            username=username,
            global_name=global_name,
            avatar=avatar,
            role=role,
        )