import discord
from discord import app_commands
from discord.ext import commands

from bot.services.show_service import ShowService
from bot.services.user_service import UserService
from bot.services.server_service import ServerService


class ShowsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="shows")
    async def list_shows_prefix(self, ctx: commands.Context):
        service = ShowService()
        try:
            shows = await service.list_shows()
            if not shows:
                await ctx.reply("No shows found.")
                return

            lines = [f"#{show.id} | {show.name} | {show.status}" for show in shows[:10]]
            await ctx.reply("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="shows", description="List shows")
    async def list_shows_slash(self, interaction: discord.Interaction):
        service = ShowService()
        try:
            await interaction.response.defer(ephemeral=True)
            shows = await service.list_shows()

            if not shows:
                await interaction.followup.send("No shows found.")
                return

            lines = [f"#{show.id} | {show.name} | {show.status}" for show in shows[:10]]
            await interaction.followup.send("\n".join(lines))
        finally:
            await service.close()

    @app_commands.command(name="show_details", description="Show details for a show")
    @app_commands.describe(show_id="Show ID")
    async def show_details(self, interaction: discord.Interaction, show_id: int):
        service = ShowService()
        try:
            await interaction.response.defer(ephemeral=True)
            show = await service.get_show(show_id)

            if not show:
                await interaction.followup.send("Show not found.")
                return

            description = show.description or "No description"
            message = (
                f"ID: {show.id}\n"
                f"Name: {show.name}\n"
                f"Status: {show.status}\n"
                f"Server ID: {show.server_id}\n"
                f"Seller DB ID: {show.seller_id}\n"
                f"Description: {description}"
            )

            await interaction.followup.send(message)
        finally:
            await service.close()

    @app_commands.command(name="create_show", description="Create a new show")
    @app_commands.describe(name="Show name", description="Optional description")
    @app_commands.guild_only()
    async def create_show(
        self,
        interaction: discord.Interaction,
        name: str,
        description: str | None = None,
    ):
        service = ShowService()
        users = UserService()
        servers = ServerService()
        try:
            await interaction.response.defer(ephemeral=True)

            if interaction.guild is None or interaction.guild_id is None:
                await interaction.followup.send("This command can only be used in a server.")
                return

            await servers.get_or_create_server(interaction.guild)

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            show = await service.create_show(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
                name=name,
                description=description,
            )

            await interaction.followup.send(f"Created show #{show.id}: {show.name}")
        finally:
            await service.close()
            await users.close()
            await servers.close()

    @app_commands.command(name="edit_show", description="Edit a show")
    @app_commands.describe(
        show_id="Show ID",
        name="New name",
        description="New description",
        status="New status",
    )
    async def edit_show(
        self,
        interaction: discord.Interaction,
        show_id: int,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ):
        service = ShowService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            show = await service.get_show(show_id)
            if not show:
                await interaction.followup.send("Show not found.")
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            if show.seller_id != seller_db_user.id:
                await interaction.followup.send("You are not allowed to edit this show.")
                return

            update_data = {
                key: value
                for key, value in {
                    "name": name,
                    "description": description,
                    "status": status,
                }.items()
                if value is not None
            }

            if not update_data:
                await interaction.followup.send("No changes provided.")
                return

            updated = await service.update_show(show_id, **update_data)
            if not updated:
                await interaction.followup.send("Update failed.")
                return

            await interaction.followup.send(f"Updated show #{updated.id}: {updated.name}")
        finally:
            await service.close()
            await users.close()

    @app_commands.command(name="delete_show", description="Delete a show")
    @app_commands.describe(show_id="Show ID")
    async def delete_show(self, interaction: discord.Interaction, show_id: int):
        service = ShowService()
        users = UserService()
        try:
            await interaction.response.defer(ephemeral=True)

            show = await service.get_show(show_id)
            if not show:
                await interaction.followup.send("Show not found.")
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            if show.seller_id != seller_db_user.id:
                await interaction.followup.send("You are not allowed to delete this show.")
                return

            ok = await service.delete_show(show_id)
            if ok:
                await interaction.followup.send(f"Deleted show #{show_id}.")
            else:
                await interaction.followup.send("Delete failed.")
        finally:
            await service.close()
            await users.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(ShowsCog(bot))