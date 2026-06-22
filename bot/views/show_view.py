import discord


class ShowView(discord.ui.View):
    def __init__(self, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Open Show', style=discord.ButtonStyle.success)
    async def open_show_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Open show action not implemented yet.', ephemeral=True)