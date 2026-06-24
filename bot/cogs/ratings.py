import discord
from discord import app_commands
from discord.ext import commands

from bot.services.rating_service import RatingService
from bot.services.user_service import UserService


class RatingsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ratings")
    async def list_ratings_prefix(self, ctx: commands.Context):
        service = RatingService()
        try:
            ratings = await service.list_ratings()
            if not ratings:
                await ctx.reply("No ratings found.")
                return

            lines = [
                f"#{rating.id} | target_db={rating.target_user_id} | score={rating.score}"
                for rating in ratings[:10]
            ]
            await ctx.reply("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="ratings", description="List ratings")
    async def list_ratings_slash(self, interaction: discord.Interaction):
        service = RatingService()
        try:
            await interaction.response.defer(ephemeral=True)
            ratings = await service.list_ratings()

            if not ratings:
                await interaction.followup.send("No ratings found.")
                return

            lines = [
                f"#{rating.id} | target_db={rating.target_user_id} | score={rating.score}"
                for rating in ratings[:10]
            ]
            await interaction.followup.send("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="create_rating", description="Create a rating")
    @app_commands.describe(
        target_user="Rated user",
        score="Score 1-5",
        comment="Optional comment",
        show_id="Optional show ID",
        order_id="Optional order ID",
    )
    @app_commands.guild_only()
    async def create_rating(
        self,
        interaction: discord.Interaction,
        target_user: discord.User,
        score: int,
        comment: str | None = None,
        show_id: int | None = None,
        order_id: int | None = None,
    ):
        ratings = RatingService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            if interaction.user.id == target_user.id:
                await interaction.followup.send("You cannot rate yourself.")
                return

            rater_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="buyer",
            )
            target_db_user = await users.get_or_create_from_discord_user(
                target_user,
                role="buyer",
            )

            rating = await ratings.create_rating(
                show_id=show_id,
                order_id=order_id,
                rater_id=rater_db_user.id,
                target_user_id=target_db_user.id,
                score=score,
                comment=comment,
            )

            await interaction.followup.send(f"Created rating #{rating.id}.")
        finally:
            await ratings.close()
            await users.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(RatingsCog(bot))