from bot.repositories.rating_repository import RatingRepository


class RatingService:
    def __init__(self, repo: RatingRepository | None = None):
        self.repo = repo or RatingRepository()

    async def list_ratings(
        self,
        target_user_id: int | None = None,
        rater_id: int | None = None,
        show_id: int | None = None,
    ):
        return await self.repo.list_ratings(
            target_user_id=target_user_id,
            rater_id=rater_id,
            show_id=show_id,
        )

    async def create_rating(
        self,
        show_id: int | None,
        order_id: int | None,
        rater_id: int,
        target_user_id: int,
        score: int,
        comment: str | None = None,
    ):
        return await self.repo.create_rating(
            show_id=show_id,
            order_id=order_id,
            rater_id=rater_id,
            target_user_id=target_user_id,
            score=score,
            comment=comment,
        )

    async def close(self):
        await self.repo.close()