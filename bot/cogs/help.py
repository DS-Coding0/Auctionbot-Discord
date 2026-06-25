from __future__ import annotations

import discord
from discord import app_commands, ui
from discord.ext import commands


HELP_COLOR = discord.Color.from_rgb(88, 101, 242)


def _server_icon_url(guild: discord.Guild | None) -> str | None:
    if guild and guild.icon:
        return guild.icon.url
    return None


def _bot_avatar_url(bot: commands.Bot) -> str | None:
    if bot.user and bot.user.display_avatar:
        return bot.user.display_avatar.url
    return None


def build_home_embed(bot: commands.Bot, guild: discord.Guild | None, user: discord.abc.User) -> discord.Embed:
    embed = discord.Embed(
        title="✨ AuctionBot Hilfezentrum",
        description=(
            "Willkommen im interaktiven Hilfebereich.\n"
            "Wähle unten im Menü einen Bereich aus, um alle wichtigen Befehle, Abläufe und Hinweise zu sehen."
        ),
        color=HELP_COLOR,
    )

    embed.set_author(
        name=f"{guild.name if guild else 'Direktnachricht'} • Help Center",
        icon_url=_server_icon_url(guild) or discord.Embed.Empty,
    )

    embed.add_field(
        name="📌 Bereiche",
        value=(
            "🎭 Shows\n"
            "📦 Items\n"
            "🔨 Auktionen\n"
            "👤 Rollen & Rechte\n"
            "💡 Tipps & Ablauf"
        ),
        inline=True,
    )

    embed.add_field(
        name="🧭 Nutzung",
        value=(
            "Nutze Slash-Commands wie `/create_show` oder `/start_show` oder `/end_show`.\n"
            "Das Menü unten wechselt zwischen den Hilfe-Seiten."
        ),
        inline=True,
    )

    embed.add_field(
        name="🖥️ Serverinfos",
        value=(
            f"**Server:** {guild.name if guild else 'Privat'}\n"
            f"**Mitglieder:** {guild.member_count if guild else '—'}\n"
            f"**Angefordert von:** {user.mention}"
        ),
        inline=False,
    )

    embed.set_thumbnail(url=_bot_avatar_url(bot) or discord.Embed.Empty)
    embed.set_footer(text="AuctionBot • Interaktive Hilfe")
    return embed


def build_shows_embed(guild: discord.Guild | None) -> discord.Embed:
    embed = discord.Embed(
        title="🎭 Shows",
        description="Shows sind dein Oberbereich für Live-Verkäufe, Sprachkanäle und spätere Auktionen.",
        color=HELP_COLOR,
    )
    embed.add_field(
        name="`/create_show`",
        value=(
            "Erstellt eine neue Show.\n"
            "**Parameter:** `name`, `date`, `time`, optional `description`\n"
            "**Beispiel:** `/create_show name:Trading Night date:2026-07-10 time:19:30`"
        ),
        inline=False,
    )
    embed.add_field(
        name="`/shows` und `/show_details`",
        value=(
            "Zeigt Shows oder Detailinfos an.\n"
            "Praktisch, um IDs, Status und Besitzer zu prüfen."
        ),
        inline=False,
    )
    embed.add_field(
        name="`/edit_show`, `/delete_show`, `/start_show`, `/end_show`",
        value=(
            "Bearbeitet, löscht, startet oder beendet deine Show.\n"
            "Beim Start wird automatisch ein Voice-Channel unter der Liveauction-Kategorie erstellt."
            "Beim Beenden wird automatisch der Voice-Channel unter der Liveauction-Kategorie geloescht."
        ),
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Show-Verwaltung")
    return embed


def build_items_embed(guild: discord.Guild | None) -> discord.Embed:
    embed = discord.Embed(
        title="📦 Items",
        description="Items sind die Produkte oder Objekte, die du später in Auktionen verwendest.",
        color=HELP_COLOR,
    )
    embed.add_field(
        name="`/create_item`",
        value=(
            "Legt ein neues Item an.\n"
            "Dazu gehören meist Titel, Beschreibung, Bild, Startpreis, Mindestgebotsschritt und optional Sofortkauf."
        ),
        inline=False,
    )
    embed.add_field(
        name="`/items`",
        value="Zeigt vorhandene Items an, meist bezogen auf eine Show oder einen Status.",
        inline=False,
    )
    embed.add_field(
        name="`/edit_item` und `/delete_item`",
        value="Aktualisiert oder entfernt bestehende Items.",
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Item-Verwaltung")
    return embed


def build_auctions_embed(guild: discord.Guild | None) -> discord.Embed:
    embed = discord.Embed(
        title="🔨 Auktionen",
        description="Auktionen machen aus einem Item einen live verkaufbaren Eintrag mit Countdown und Geboten.",
        color=HELP_COLOR,
    )
    embed.add_field(
        name="`/create_auction`",
        value=(
            "Erstellt einen Auktionsentwurf.\n"
            "Damit verbindest du ein Item mit einer Show."
        ),
        inline=False,
    )
    embed.add_field(
        name="`/start_auction`",
        value=(
            "Startet die Auktion mit Laufzeit und Reset-Zeit.\n"
            "Wenn kurz vor Ende ein Gebot kommt, kann der Countdown erneut auf das Reset-Fenster springen."
        ),
        inline=False,
    )
    embed.add_field(
        name="Bieten & Sofortkauf",
        value=(
            "In der Live-Auktion können Nutzer über Buttons bieten.\n"
            "Wenn aktiviert, ist auch `Instant Buy` möglich."
        ),
        inline=False,
    )
    embed.add_field(
        name="Live-Countdown",
        value=(
            "Die Auktionsansicht kann sich automatisch aktualisieren, "
            "damit die Restzeit im Embed live sichtbar bleibt."
        ),
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Auktionssystem")
    return embed


def build_roles_embed(guild: discord.Guild | None) -> discord.Embed:
    embed = discord.Embed(
        title="👤 Rollen & Rechte",
        description="Nicht jeder Nutzer darf jede Aktion ausführen. Einige Befehle hängen direkt am Besitzer einer Show oder Auktion.",
        color=HELP_COLOR,
    )
    embed.add_field(
        name="🛍️ Käufer",
        value=(
            "Käufer können an Auktionen teilnehmen, bieten und – falls erlaubt – Sofortkäufe auslösen."
        ),
        inline=False,
    )
    embed.add_field(
        name="🏪 Verkäufer",
        value=(
            "Verkäufer erstellen Shows, legen Items an, starten Shows und verwalten eigene Auktionen."
        ),
        inline=False,
    )
    embed.add_field(
        name="🔒 Eigentümer-Prinzip",
        value=(
            "Nur der Besitzer einer Show sollte sie bearbeiten, löschen oder starten dürfen.\n"
            "Dasselbe gilt für zugehörige Auktionsabläufe."
        ),
        inline=False,
    )
    embed.add_field(
        name="⚠️ Wichtiger Hinweis",
        value=(
            "Ein Verkäufer darf nicht auf die eigene Auktion bieten.\n"
            "Zusätzlich braucht der Bot passende Serverrechte, etwa zum Erstellen von Channels."
        ),
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Rechte und Rollen")
    return embed


def build_tips_embed(guild: discord.Guild | None) -> discord.Embed:
    embed = discord.Embed(
        title="💡 Tipps & Ablauf",
        description="So nutzt du den Bot am sinnvollsten und vermeidest typische Fehler.",
        color=HELP_COLOR,
    )
    embed.add_field(
        name="Empfohlener Ablauf",
        value=(
            "1. Show erstellen\n"
            "2. Items anlegen\n"
            "3. Auktion als Draft anlegen\n"
            "4. Show starten\n"
            "5. Auktion starten\n"
            "6. Live bieten lassen"
        ),
        inline=False,
    )
    embed.add_field(
        name="Datums- und Zeitformat",
        value=(
            "Achte bei Shows auf das richtige Format.\n"
            "`date`: `YYYY-MM-DD`\n"
            "`time`: `HH:MM`"
        ),
        inline=False,
    )
    embed.add_field(
        name="Auktionswerte",
        value=(
            "`duration_seconds` und `reset_seconds` müssen gültige positive Zahlen sein.\n"
            "`reset_seconds` darf nicht größer als `duration_seconds` sein."
        ),
        inline=False,
    )
    embed.add_field(
        name="Saubere Struktur",
        value=(
            "Nutze klare Show-Namen und ordentlich gepflegte Items, "
            "damit Voice-Channels, Embeds und Auktionen sauber aussehen."
        ),
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Tipps zur Nutzung")
    return embed


class HelpCategorySelect(ui.Select):
    def __init__(self, bot: commands.Bot, author_id: int, guild: discord.Guild | None):
        self.bot = bot
        self.author_id = author_id
        self.guild = guild

        options = [
            discord.SelectOption(
                label="Startseite",
                value="home",
                description="Allgemeine Übersicht und Serverinfos",
                emoji="🏠",
            ),
            discord.SelectOption(
                label="Shows",
                value="shows",
                description="Befehle rund um Shows",
                emoji="🎭",
            ),
            discord.SelectOption(
                label="Items",
                value="items",
                description="Item-Verwaltung und Nutzung",
                emoji="📦",
            ),
            discord.SelectOption(
                label="Auktionen",
                value="auctions",
                description="Auktionen, Gebote und Countdown",
                emoji="🔨",
            ),
            discord.SelectOption(
                label="Rollen & Rechte",
                value="roles",
                description="Käufer, Verkäufer und Berechtigungen",
                emoji="👤",
            ),
            discord.SelectOption(
                label="Tipps & Ablauf",
                value="tips",
                description="Hilfreiche Hinweise für die Nutzung",
                emoji="💡",
            ),
        ]

        super().__init__(
            placeholder="Wähle einen Hilfebereich aus …",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Dieses Hilfe-Menü gehört nicht dir.",
                ephemeral=True,
            )
            return

        value = self.values[0]

        if value == "home":
            embed = build_home_embed(self.bot, self.guild, interaction.user)
        elif value == "shows":
            embed = build_shows_embed(self.guild)
        elif value == "items":
            embed = build_items_embed(self.guild)
        elif value == "auctions":
            embed = build_auctions_embed(self.guild)
        elif value == "roles":
            embed = build_roles_embed(self.guild)
        else:
            embed = build_tips_embed(self.guild)

        await interaction.response.edit_message(embed=embed, view=self.view)


class PremiumHelpView(ui.View):
    def __init__(self, bot: commands.Bot, author_id: int, guild: discord.Guild | None, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author_id = author_id
        self.guild = guild
        self.message: discord.Message | None = None
        self.add_item(HelpCategorySelect(bot=bot, author_id=author_id, guild=guild))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Du kannst dieses Hilfe-Menü nicht bedienen.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(label="Startseite", emoji="🏠", style=discord.ButtonStyle.primary)
    async def home_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = build_home_embed(self.bot, self.guild, interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Support", emoji="🛠️", style=discord.ButtonStyle.secondary)
    async def support_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="🛠️ Support",
            description=(
                "Wenn etwas nicht funktioniert, prüfe zuerst:\n"
                "- Sind die benötigten Berechtigungen vorhanden?\n"
                "- Existiert die Show / das Item / die Auktion wirklich?\n"
                "- Verwendest du das richtige Datums- oder Zahlenformat?\n"
                "- Gehört dir die Show oder Auktion, die du verwalten willst?"
            ),
            color=HELP_COLOR,
        )
        if self.guild:
            embed.set_author(
                name=f"{self.guild.name} • Support",
                icon_url=_server_icon_url(self.guild) or discord.Embed.Empty,
            )
        embed.set_footer(text="AuctionBot • Fehler zuerst strukturiert prüfen")
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Schließen", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: ui.Button):
        for child in self.children:
            child.disabled = True

        embed = discord.Embed(
            title="🔒 Hilfe geschlossen",
            description="Das Hilfe-Menü wurde beendet.",
            color=discord.Color.red(),
        )
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        if self.message:
            try:
                timeout_embed = discord.Embed(
                    title="⏳ Hilfe abgelaufen",
                    description="Dieses Hilfe-Menü ist abgelaufen. Öffne `/help` erneut.",
                    color=discord.Color.orange(),
                )
                await self.message.edit(embed=timeout_embed, view=self)
            except discord.HTTPException:
                pass


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Öffnet das interaktive Hilfezentrum")
    async def help_slash(self, interaction: discord.Interaction):
        view = PremiumHelpView(
            bot=self.bot,
            author_id=interaction.user.id,
            guild=interaction.guild,
        )
        embed = build_home_embed(self.bot, interaction.guild, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        try:
            view.message = await interaction.original_response()
        except discord.HTTPException:
            view.message = None

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context):
        view = PremiumHelpView(
            bot=self.bot,
            author_id=ctx.author.id,
            guild=ctx.guild,
        )
        embed = build_home_embed(self.bot, ctx.guild, ctx.author)
        message = await ctx.reply(embed=embed, view=view)
        view.message = message


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))