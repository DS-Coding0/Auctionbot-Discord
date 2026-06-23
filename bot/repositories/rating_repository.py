from db.repository import Repository


class RatingRepository(Repository):
    def create_rating(
        self,
        show_id: int | None,
        order_id: int | None,
        rater_id: int,
        target_user_id: int,
        score: int,
        comment: str | None = None,
    ):
        return super().create_rating(
            show_id=show_id,
            order_id=order_id,
            rater_id=rater_id,
            target_user_id=target_user_id,
            score=score,
            comment=comment,
        )