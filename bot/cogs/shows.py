from __future__ import annotations

import re
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from discord import app_commands, ui
from discord.ext import commands

from bot.services.server_service import ServerService
from bot.services.show_service import ShowService
from bot.services.user_service import UserService


LIVEAUCTION_CATEGORY_ID = 1519260742837342209
PANEL_COLOR = discord.Color.blurple()

ALLOWED_SHOW_STATUSES = {
    "draft": "draft",
    "planned": "planned",
    "live": "live",
    "ended": "ended",
    "cancelled": "cancelled",
}

EDITABLE_SHOW_STATUSES = {
    "draft": "draft",
    "planned": "planned",
    "cancelled": "cancelled",
}

STATUS_LABELS = {
    "draft": "🟡 draft",
    "planned": "🟡 planned",
    "live": "🟢 live",
    "ended": "🔴 ended",
    "cancelled": "⚫ cancelled",
}


def slugify_channel_name(value: str) -> str:
    value = value.lower().strip()
    value = value.replace(" ", "-")
    value = re.sub(r"[^a-z0-9\-_]", "", value)
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-")
    return value or "show"


def normalize_show_status(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if not normalized:
        return None

    return ALLOWED_SHOW_STATUSES.get(normalized)


def normalize_editable_show_status(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower()
    if not normalized:
        return None

    return EDITABLE_SHOW_STATUSES.get(normalized)


def show_status_emoji(status: str | None) -> str:
    normalized = (status or "").lower()
    if normalized == "live":
        return "🟢"
    if normalized in {"draft", "planned"}:
        return "🟡"
    if normalized == "ended":
        return "🔴"
    if normalized == "cancelled":
        return "⚫"
    return "⚪"


def format_show_status(status: str | None) -> str:
    normalized = (status or "").lower()
    return STATUS_LABELS.get(normalized, f"⚪ {status or 'unknown'}")


def format_show_datetime(dt) -> str:
    if dt is None:
        return "—"
    if getattr(dt, "tzinfo", None) is None:
        return dt.strftime("%d-%m-%Y %H:%M")
    return dt.astimezone(ZoneInfo("Europe/Berlin")).strftime("%d-%m-%Y %H:%M")


def build_show_panel_embed(guild: discord.Guild | None, user: discord.abc.User) -> discord.Embed:
    embed = discord.Embed(
        title="🎭 Show-Menü",
        description=(
            "Verwalte deine Shows über die Buttons unten.\n"
            "Alle wichtigen Show-Aktionen laufen über dieses zentrale Panel."
        ),
        color=PANEL_COLOR,
    )
    embed.add_field(
        name="Aktionen",
        value=(
            "➕ Show anlegen\n"
            "📋 Shows anzeigen\n"
            "🔎 Details anzeigen\n"
            "▶️ Show starten\n"
            "⏹️ Show beenden\n"
            "✏️ Show bearbeiten\n"
            "🗑️ Show löschen"
        ),
        inline=False,
    )
    embed.add_field(
        name="Hinweis",
        value=(
            "Für Details, Starten, Beenden, Bearbeiten und Löschen "
            "wählst du eine vorhandene Show direkt aus."
        ),
        inline=False,
    )
    if guild:
        embed.set_footer(text=f"{guild.name} • Angefordert von {user.display_name}")
    return embed


def build_shows_list_embed(shows: list, title: str = "📋 Shows") -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description="Hier siehst du die aktuell verfügbaren Shows.",
        color=PANEL_COLOR,
    )

    if not shows:
        embed.description = "Keine Shows gefunden."
        return embed

    for show in shows[:10]:
        starts_at = format_show_datetime(getattr(show, "starts_at", None))
        description = getattr(show, "description", None) or "Keine Beschreibung"

        embed.add_field(
            name=f"{show_status_emoji(getattr(show, 'status', None))} #{show.id} • {show.name}",
            value=(
                f"**Status:** {format_show_status(getattr(show, 'status', 'unknown'))}\n"
                f"**Start:** {starts_at}\n"
                f"**Beschreibung:** {description[:120]}"
            ),
            inline=False,
        )

    embed.set_footer(text=f"{len(shows)} Show(s) gefunden")
    return embed


def build_show_details_embed(show) -> discord.Embed:
    description = getattr(show, "description", None) or "No description"
    embed = discord.Embed(
        title=f"🔎 Show #{show.id} • {show.name}",
        color=PANEL_COLOR,
    )
    embed.add_field(
        name="Status",
        value=format_show_status(getattr(show, "status", None)),
        inline=True,
    )
    embed.add_field(
        name="Start",
        value=format_show_datetime(getattr(show, "starts_at", None)),
        inline=True,
    )
    embed.add_field(
        name="Seller DB ID",
        value=str(getattr(show, "seller_id", "—")),
        inline=True,
    )
    embed.add_field(
        name="Server ID",
        value=str(getattr(show, "server_id", "—")),
        inline=True,
    )
    embed.add_field(
        name="Voice Channel ID",
        value=str(getattr(show, "voice_channel_id", None) or "—"),
        inline=True,
    )
    embed.add_field(
        name="Beschreibung",
        value=description[:1024],
        inline=False,
    )
    return embed


class CreateShowModal(ui.Modal, title="Show anlegen"):
    name = ui.TextInput(
        label="Show-Name",
        placeholder="z. B. Trading Night",
        required=True,
        max_length=100,
    )
    date = ui.TextInput(
        label="Datum",
        placeholder="DD-MM-YYYY",
        required=True,
        max_length=10,
    )
    time = ui.TextInput(
        label="Uhrzeit",
        placeholder="HH:MM",
        required=True,
        max_length=5,
    )
    description = ui.TextInput(
        label="Beschreibung",
        placeholder="Optional",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        service = ShowService()
        users = UserService()
        servers = ServerService()

        try:
            if interaction.guild is None or interaction.guild_id is None:
                await interaction.response.send_message(
                    "This command can only be used in a server.",
                    ephemeral=True,
                )
                return

            try:
                starts_at = datetime.strptime(f"{self.date.value} {self.time.value}", "%d-%m-%Y %H:%M")
                starts_at = starts_at.replace(tzinfo=ZoneInfo("Europe/Berlin"))
            except ValueError:
                await interaction.response.send_message(
                    "Invalid date/time format. Use date as DD-MM-YYYY and time as HH:MM.",
                    ephemeral=True,
                )
                return

            await servers.get_or_create_server(interaction.guild)

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            show = await service.create_show(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
                name=self.name.value.strip(),
                description=self.description.value.strip() or None,
                starts_at=starts_at,
            )

            await interaction.response.send_message(
                f"✅ Created show #{show.id}: {show.name} at {starts_at.strftime('%d-%m-%Y %H:%M')}",
                ephemeral=True,
            )
        finally:
            await service.close()
            await users.close()
            await servers.close()


class EditShowModal(ui.Modal, title="Show bearbeiten"):
    name = ui.TextInput(
        label="Neuer Name",
        required=False,
        max_length=100,
    )
    description = ui.TextInput(
        label="Neue Beschreibung",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500,
    )
    status = ui.TextInput(
        label="Neuer Status",
        required=False,
        placeholder="draft | planned | cancelled",
        max_length=32,
    )

    def __init__(self, show):
        super().__init__()
        self.show_id = show.id

        self.name.default = getattr(show, "name", "") or ""
        self.description.default = getattr(show, "description", "") or ""

        current_status = (getattr(show, "status", "") or "").lower()
        self.status.default = current_status if current_status in EDITABLE_SHOW_STATUSES else ""

    async def on_submit(self, interaction: discord.Interaction):
        service = ShowService()
        users = UserService()

        try:
            show = await service.get_show(self.show_id)
            if not show:
                await interaction.response.send_message("Show not found.", ephemeral=True)
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            if show.seller_id != seller_db_user.id:
                await interaction.response.send_message(
                    "You are not allowed to edit this show.",
                    ephemeral=True,
                )
                return

            current_status = (getattr(show, "status", "") or "").lower()

            if current_status == "live":
                await interaction.response.send_message(
                    "Eine live Show kann nicht über Bearbeiten geändert werden. Nutze zuerst 'Beenden'.",
                    ephemeral=True,
                )
                return

            raw_status = self.status.value.strip()
            normalized_status = normalize_editable_show_status(raw_status)

            if raw_status and normalized_status is None:
                allowed = ", ".join(EDITABLE_SHOW_STATUSES.keys())
                await interaction.response.send_message(
                    (
                        "Ungültiger Status für Bearbeiten. "
                        f"Erlaubt sind nur: {allowed}. "
                        "Für 'live' nutze Starten, für 'ended' nutze Beenden."
                    ),
                    ephemeral=True,
                )
                return

            if current_status == "ended" and normalized_status in {"draft", "planned"}:
                await interaction.response.send_message(
                    "Eine beendete Show kann nicht zurück auf draft oder planned gesetzt werden.",
                    ephemeral=True,
                )
                return

            update_data = {
                "name": self.name.value.strip() or None,
                "description": self.description.value.strip() or None,
                "status": normalized_status,
            }

            updated = await service.update_show(self.show_id, **update_data)
            if not updated:
                await interaction.response.send_message("Update failed.", ephemeral=True)
                return

            embed = discord.Embed(
                title="✏️ Show aktualisiert",
                description=f"Show #{updated.id} wurde erfolgreich aktualisiert.",
                color=discord.Color.green(),
            )
            embed.add_field(name="Name", value=updated.name, inline=False)
            embed.add_field(
                name="Status",
                value=format_show_status(getattr(updated, "status", None)),
                inline=False,
            )
            embed.add_field(
                name="Beschreibung",
                value=(getattr(updated, "description", None) or "Keine Beschreibung")[:1024],
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            await service.close()
            await users.close()


class DeleteConfirmView(ui.View):
    def __init__(self, *, author_id: int, show_id: int, show_name: str, timeout: float | None = 120):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.show_id = show_id
        self.show_name = show_name

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Du kannst diese Löschbestätigung nicht benutzen.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(label="Ja, löschen", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: ui.Button):
        service = ShowService()
        users = UserService()

        try:
            show = await service.get_show(self.show_id)
            if not show:
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Nicht gefunden",
                        description="Die Show existiert nicht mehr.",
                        color=discord.Color.red(),
                    ),
                    view=None,
                )
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            if show.seller_id != seller_db_user.id:
                await interaction.response.send_message(
                    "You are not allowed to delete this show.",
                    ephemeral=True,
                )
                return

            ok = await service.delete_show(self.show_id)
            if not ok:
                await interaction.response.send_message("Delete failed.", ephemeral=True)
                return

            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="🗑️ Show gelöscht",
                    description=f"Show #{self.show_id} • {self.show_name} wurde gelöscht.",
                    color=discord.Color.red(),
                ),
                view=None,
            )
        finally:
            await service.close()
            await users.close()

    @ui.button(label="Abbrechen", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="Abgebrochen",
                description="Die Show wurde nicht gelöscht.",
                color=discord.Color.light_grey(),
            ),
            view=None,
        )


class ShowSelect(discord.ui.Select):
    def __init__(self, *, bot: commands.Bot, author_id: int, action: str, shows: list):
        self.bot = bot
        self.author_id = author_id
        self.action = action

        options = []
        for show in shows[:25]:
            emoji = show_status_emoji(getattr(show, "status", None))
            starts_at = format_show_datetime(getattr(show, "starts_at", None))
            options.append(
                discord.SelectOption(
                    label=str(show.name)[:100],
                    value=str(show.id),
                    description=f"{emoji} #{show.id} • {starts_at}"[:100],
                )
            )

        super().__init__(
            placeholder="Wähle eine Show aus …",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Du kannst diese Auswahl nicht benutzen.",
                ephemeral=True,
            )
            return

        show_id = int(self.values[0])

        service = ShowService()
        users = UserService()

        try:
            if interaction.guild is None:
                await interaction.response.send_message(
                    "This command can only be used in a server.",
                    ephemeral=True,
                )
                return

            show = await service.get_show(show_id)
            if not show:
                await interaction.response.send_message("Show not found.", ephemeral=True)
                return

            if self.action == "details":
                embed = build_show_details_embed(show)
                await interaction.response.edit_message(embed=embed, view=self.view)
                return

            seller_db_user = await users.get_or_create_from_discord_user(
                interaction.user,
                role="seller",
            )

            if show.seller_id != seller_db_user.id:
                await interaction.response.send_message(
                    "You are not allowed to manage this show.",
                    ephemeral=True,
                )
                return

            if self.action == "edit":
                current_status = (getattr(show, "status", "") or "").lower()

                if current_status == "live":
                    await interaction.response.send_message(
                        "Eine live Show kann nicht direkt bearbeitet werden. Beende sie zuerst.",
                        ephemeral=True,
                    )
                    return

                await interaction.response.send_modal(EditShowModal(show))
                return

            if self.action == "delete":
                embed = discord.Embed(
                    title="⚠️ Löschung bestätigen",
                    description=(
                        f"Möchtest du die Show **#{show.id} • {show.name}** wirklich löschen?\n"
                        "Diese Aktion kann nicht rückgängig gemacht werden."
                    ),
                    color=discord.Color.orange(),
                )
                view = DeleteConfirmView(
                    author_id=self.author_id,
                    show_id=show.id,
                    show_name=show.name,
                )
                await interaction.response.edit_message(embed=embed, view=view)
                return

            if self.action == "start":
                if show.status == "live":
                    await interaction.response.send_message("This show is already live.", ephemeral=True)
                    return

                category = interaction.guild.get_channel(LIVEAUCTION_CATEGORY_ID)
                if not isinstance(category, discord.CategoryChannel):
                    await interaction.response.send_message("Liveauction category not found.", ephemeral=True)
                    return

                bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
                if bot_member is None or not bot_member.guild_permissions.manage_channels:
                    await interaction.response.send_message("I need 'Manage Channels' permission.", ephemeral=True)
                    return

                if getattr(show, "voice_channel_id", None):
                    existing_channel = interaction.guild.get_channel(show.voice_channel_id)
                    if existing_channel is None:
                        existing_channel = self.bot.get_channel(show.voice_channel_id)

                    if existing_channel is not None:
                        await interaction.response.send_message(
                            f"This show is already linked to voice channel {existing_channel.mention}.",
                            ephemeral=True,
                        )
                        return

                show_part = slugify_channel_name(show.name)[:70]
                user_part = slugify_channel_name(interaction.user.name)[:25]
                channel_name = f"{show_part}-{user_part}"[:100]

                voice_channel = await category.create_voice_channel(
                    name=channel_name,
                    reason=f"Show #{show.id} started by {interaction.user}",
                )

                updated = await service.start_show(
                    show_id=show_id,
                    voice_channel_id=voice_channel.id,
                )

                embed = discord.Embed(
                    title="▶️ Show gestartet",
                    description=f"Show #{updated.id} wurde gestartet.\nVoice Channel: {voice_channel.mention}",
                    color=discord.Color.green(),
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            if self.action == "end":
                if show.status != "live":
                    await interaction.response.send_message("This show is not currently live.", ephemeral=True)
                    return

                bot_member = interaction.guild.get_member(self.bot.user.id) if self.bot.user else None
                if bot_member is None or not bot_member.guild_permissions.manage_channels:
                    await interaction.response.send_message("I need 'Manage Channels' permission.", ephemeral=True)
                    return

                deleted_channel_name = None

                if getattr(show, "voice_channel_id", None):
                    channel = interaction.guild.get_channel(show.voice_channel_id)
                    if channel is None:
                        channel = self.bot.get_channel(show.voice_channel_id)

                    if channel is not None:
                        deleted_channel_name = channel.name
                        await channel.delete(reason=f"Show #{show.id} ended by {interaction.user}")

                updated = await service.update_show(
                    show_id,
                    status="ended",
                    voice_channel_id=None,
                )

                if updated is None:
                    await interaction.response.send_message("Failed to end show.", ephemeral=True)
                    return

                text = (
                    f"Show #{updated.id} wurde beendet.\n"
                    f"Gelöschter Voice Channel: `{deleted_channel_name}`"
                    if deleted_channel_name
                    else f"Show #{updated.id} wurde beendet.\nKein Voice Channel gefunden."
                )

                embed = discord.Embed(
                    title="⏹️ Show beendet",
                    description=text,
                    color=discord.Color.orange(),
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return

            await interaction.response.send_message("Unknown action.", ephemeral=True)
        finally:
            await service.close()
            await users.close()


class ShowSelectView(ui.View):
    def __init__(
        self,
        *,
        bot: commands.Bot,
        author_id: int,
        action: str,
        shows: list,
        timeout: float | None = 120,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author_id = author_id
        self.action = action

        if shows:
            self.add_item(ShowSelect(bot=bot, author_id=author_id, action=action, shows=shows))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Du kannst diese Auswahl nicht benutzen.", ephemeral=True)
            return False
        return True


async def send_show_select_menu(
    interaction: discord.Interaction,
    *,
    bot: commands.Bot,
    author_id: int,
    action: str,
    title: str,
):
    service = ShowService()
    users = UserService()

    try:
        if interaction.guild is None or interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        seller_db_user = await users.get_or_create_from_discord_user(
            interaction.user,
            role="seller",
        )

        if action == "details":
            shows = await service.list_shows(server_id=interaction.guild_id)
        elif action == "start":
            shows = await service.list_shows(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
            )
            shows = [show for show in shows if getattr(show, "status", None) != "live"]
        elif action == "end":
            shows = await service.list_shows(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
                status="live",
            )
        elif action == "edit":
            shows = await service.list_shows(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
            )
            shows = [show for show in shows if getattr(show, "status", None) != "live"]
        elif action == "delete":
            shows = await service.list_shows(
                server_id=interaction.guild_id,
                seller_id=seller_db_user.id,
            )
        else:
            shows = await service.list_shows(server_id=interaction.guild_id)

        if not shows:
            await interaction.response.send_message("Keine passenden Shows gefunden.", ephemeral=True)
            return

        embed = build_shows_list_embed(shows, title=title)
        view = ShowSelectView(
            bot=bot,
            author_id=author_id,
            action=action,
            shows=shows,
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    finally:
        await service.close()
        await users.close()


class ShowPanelView(ui.View):
    def __init__(self, bot: commands.Bot, author_id: int, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author_id = author_id
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Du kannst dieses Show-Menü nicht bedienen.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(label="Show anlegen", emoji="➕", style=discord.ButtonStyle.success, row=0)
    async def create_show_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(CreateShowModal())

    @ui.button(label="Shows anzeigen", emoji="📋", style=discord.ButtonStyle.primary, row=0)
    async def list_shows_button(self, interaction: discord.Interaction, button: ui.Button):
        service = ShowService()
        try:
            if interaction.guild is None or interaction.guild_id is None:
                await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
                return
            shows = await service.list_shows(server_id=interaction.guild_id)
            embed = build_shows_list_embed(shows)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        finally:
            await service.close()

    @ui.button(label="Details", emoji="🔎", style=discord.ButtonStyle.secondary, row=0)
    async def details_button(self, interaction: discord.Interaction, button: ui.Button):
        await send_show_select_menu(
            interaction,
            bot=self.bot,
            author_id=self.author_id,
            action="details",
            title="🔎 Show auswählen",
        )

    @ui.button(label="Starten", emoji="▶️", style=discord.ButtonStyle.success, row=1)
    async def start_show_button(self, interaction: discord.Interaction, button: ui.Button):
        await send_show_select_menu(
            interaction,
            bot=self.bot,
            author_id=self.author_id,
            action="start",
            title="▶️ Show zum Starten auswählen",
        )

    @ui.button(label="Beenden", emoji="⏹️", style=discord.ButtonStyle.danger, row=1)
    async def end_show_button(self, interaction: discord.Interaction, button: ui.Button):
        await send_show_select_menu(
            interaction,
            bot=self.bot,
            author_id=self.author_id,
            action="end",
            title="⏹️ Live-Show zum Beenden auswählen",
        )

    @ui.button(label="Bearbeiten", emoji="✏️", style=discord.ButtonStyle.primary, row=1)
    async def edit_show_button(self, interaction: discord.Interaction, button: ui.Button):
        await send_show_select_menu(
            interaction,
            bot=self.bot,
            author_id=self.author_id,
            action="edit",
            title="✏️ Show zum Bearbeiten auswählen",
        )

    @ui.button(label="Löschen", emoji="🗑️", style=discord.ButtonStyle.danger, row=1)
    async def delete_show_button(self, interaction: discord.Interaction, button: ui.Button):
        await send_show_select_menu(
            interaction,
            bot=self.bot,
            author_id=self.author_id,
            action="delete",
            title="🗑️ Show zum Löschen auswählen",
        )

    @ui.button(label="Aktualisieren", emoji="🔄", style=discord.ButtonStyle.secondary, row=2)
    async def refresh_button(self, interaction: discord.Interaction, button: ui.Button):
        embed = build_show_panel_embed(interaction.guild, interaction.user)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass


class ShowsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="show", description="Öffnet das interaktive Show-Menü")
    @app_commands.guild_only()
    async def show_panel(self, interaction: discord.Interaction):
        view = ShowPanelView(bot=self.bot, author_id=interaction.user.id)
        embed = build_show_panel_embed(interaction.guild, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        try:
            view.message = await interaction.original_response()
        except discord.HTTPException:
            view.message = None


async def setup(bot: commands.Bot):
    await bot.add_cog(ShowsCog(bot))