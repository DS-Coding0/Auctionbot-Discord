from bot.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository | None = None):
        self.repo = repo or UserRepository()

    async def get_or_create_from_discord_user(
        self,
        user,
        role: str = "buyer",
    ):
        avatar = user.display_avatar.url if user.display_avatar else None

        return await self.repo.get_or_create_from_discord(
            discord_id=str(user.id),
            username=user.name,
            global_name=user.global_name,
            avatar=avatar,
            role=role,
        )

    async def get_or_create_from_discord(
        self,
        discord_id: str,
        username: str,
        global_name: str | None = None,
        avatar: str | None = None,
        role: str = "buyer",
    ):
        return await self.repo.get_or_create_from_discord(
            discord_id=discord_id,
            username=username,
            global_name=global_name,
            avatar=avatar,
            role=role,
        )

    async def get_user(self, user_id: int):
        return await self.repo.get_user(user_id)

    async def get_user_by_discord_id(self, discord_id: str):
        return await self.repo.get_user_by_discord_id(discord_id)

    async def close(self):
        await self.repo.close()