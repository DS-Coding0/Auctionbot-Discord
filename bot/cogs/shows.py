from discord import app_commands
from discord.ext import commands

from bot.services.show_service import ShowService


class ShowsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.service = ShowService()

    @commands.command(name='shows')
    async def list_shows_prefix(self, ctx: commands.Context):
        shows = self.service.list_shows()
        if not shows:
            return await ctx.reply('No shows found.')
        lines = [f'#{show.id} | {show.name} | {show.status}' for show in shows[:10]]
        await ctx.reply('\n'.join(lines))

    @app_commands.command(name='shows', description='List shows')
    async def list_shows_slash(self, interaction):
        shows = self.service.list_shows()
        if not shows:
            return await interaction.response.send_message('No shows found.', ephemeral=True)
        lines = [f'#{show.id} | {show.name} | {show.status}' for show in shows[:10]]
        await interaction.response.send_message('\n'.join(lines), ephemeral=True)

    @app_commands.command(name='show_details', description='Show details for a show')
    @app_commands.describe(show_id='Show ID')
    async def show_details(self, interaction, show_id: int):
        show = self.service.get_show(show_id)
        if not show:
            return await interaction.response.send_message('Show not found.', ephemeral=True)
        description = show.description or 'No description'
        message = (
            f'ID: {show.id}\n'
            f'Name: {show.name}\n'
            f'Status: {show.status}\n'
            f'Server ID: {show.server_id}\n'
            f'Seller ID: {show.seller_id}\n'
            f'Description: {description}'
        )
        await interaction.response.send_message(message, ephemeral=True)

    @app_commands.command(name='create_show', description='Create a new show')
    @app_commands.describe(name='Show name', description='Optional description')
    async def create_show(self, interaction, name: str, description: str | None = None):
        server_id = interaction.guild_id
        if not server_id:
            return await interaction.response.send_message('This command can only be used in a server.', ephemeral=True)
        seller_id = interaction.user.id
        show = self.service.create_show(server_id=server_id, seller_id=seller_id, name=name, description=description)
        await interaction.response.send_message(f'Created show #{show.id}: {show.name}', ephemeral=True)

    @app_commands.command(name='edit_show', description='Edit a show')
    @app_commands.describe(show_id='Show ID', name='New name', description='New description', status='New status')
    async def edit_show(self, interaction, show_id: int, name: str | None = None, description: str | None = None, status: str | None = None):
        show = self.service.get_show(show_id)
        if not show:
            return await interaction.response.send_message('Show not found.', ephemeral=True)
        if show.seller_id != interaction.user.id:
            return await interaction.response.send_message('You are not allowed to edit this show.', ephemeral=True)
        updated = self.service.update_show(show_id, **{k: v for k, v in {'name': name, 'description': description, 'status': status}.items() if v is not None})
        await interaction.response.send_message(f'Updated show #{updated.id}: {updated.name}', ephemeral=True)

    @app_commands.command(name='delete_show', description='Delete a show')
    @app_commands.describe(show_id='Show ID')
    async def delete_show(self, interaction, show_id: int):
        show = self.service.get_show(show_id)
        if not show:
            return await interaction.response.send_message('Show not found.', ephemeral=True)
        if show.seller_id != interaction.user.id:
            return await interaction.response.send_message('You are not allowed to delete this show.', ephemeral=True)
        ok = self.service.delete_show(show_id)
        if ok:
            await interaction.response.send_message(f'Deleted show #{show_id}.', ephemeral=True)
        else:
            await interaction.response.send_message('Delete failed.', ephemeral=True)


async def setup(bot):
    cog = ShowsCog(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.list_shows_slash)
    bot.tree.add_command(cog.show_details)
    bot.tree.add_command(cog.create_show)
    bot.tree.add_command(cog.edit_show)
    bot.tree.add_command(cog.delete_show)