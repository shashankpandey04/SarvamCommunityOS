import discord
from discord.ext import commands

from config import DISCORD_TOKEN, SARVAM_API_KEY
from sarvam_client import SarvamService
from api import app

class CommunityOSBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        # --------------------------------------------------
        # Single shared SarvamAI instance — every cog uses
        # self.bot.sarvam instead of creating its own.
        # --------------------------------------------------
        self.sarvam = SarvamService(SARVAM_API_KEY)

        app.state.discord_bot = self
        
        # --------------------------------------------------
        # Load all cogs via load_extension so each module
        # gets a proper setup() call.
        # --------------------------------------------------
        extensions = [
            "cogs.api_cog",
            "cogs.ask",
            "cogs.feedback",
            "cogs.escalation",
            "modules.contributor_cog",
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"[BOT] loaded: {ext}")
            except Exception as exc:
                print(f"[BOT] failed to load {ext}: {exc}")

        await self.tree.sync()
        print("[BOT] slash commands synced.")


bot = CommunityOSBot()


@bot.event
async def on_ready():
    print(f"[BOT] logged in as {bot.user}")
    print("[BOT] CommunityOS is online.")


bot.run(DISCORD_TOKEN)
