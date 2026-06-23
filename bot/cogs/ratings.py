import discord
from discord import app_commands
from discord.ext import commands

from bot.services.rating_service import RatingService


class RatingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = RatingService()

    @commands.command(name="ratings")
    async def list_ratings_prefix(self, ctx: commands.Context):
        ratings = self.service.list_ratings()
        if not ratings:
            return await ctx.reply("No ratings found.")

        lines = [
            f"#{rating.id} | target={rating.target_user_id} | score={rating.score}"
            for rating in ratings[:10]
        ]
        await ctx.reply("\n".join(lines))

    @app_commands.command(name="ratings", description="List ratings")
    async def list_ratings_slash(self, interaction: discord.Interaction):
        ratings = self.service.list_ratings()
        if not ratings:
            return await interaction.response.send_message(
                "No ratings found.",
                ephemeral=True,
            )

        lines = [
            f"#{rating.id} | target={rating.target_user_id} | score={rating.score}"
            for rating in ratings[:10]
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(name="create_rating", description="Create a rating")
    @app_commands.describe(
        target_user_id="Rated user ID",
        score="Score 1-5",
        comment="Optional comment",
    )
    async def create_rating(
        self,
        interaction: discord.Interaction,
        target_user_id: int,
        score: int,
        comment: str | None = None,
        show_id: int | None = None,
        order_id: int | None = None,
    ):
        rating = self.service.create_rating(
            show_id=show_id,
            order_id=order_id,
            rater_id=interaction.user.id,
            target_user_id=target_user_id,
            score=score,
            comment=comment,
        )

        await interaction.response.send_message(
            f"Created rating #{rating.id}.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(RatingsCog(bot))