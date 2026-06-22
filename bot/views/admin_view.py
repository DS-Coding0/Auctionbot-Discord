import discord


class AdminView(discord.ui.View):
    def __init__(self, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label='Ban Buyer', style=discord.ButtonStyle.danger)
    async def ban_buyer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Ban buyer action not implemented yet.', ephemeral=True)