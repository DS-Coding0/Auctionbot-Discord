from discord.ext import tasks


class ReminderLoops:
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=5)
    async def send_reminders(self):
        pass

    @send_reminders.before_loop
    async def before_send_reminders(self):
        await self.bot.wait_until_ready()