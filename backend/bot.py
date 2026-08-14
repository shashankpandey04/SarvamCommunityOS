import discord

from discord.ext import commands

from config import DISCORD_TOKEN
from discord_bot import CommunityOS


class CommunityOSBot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.default()

        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):

        await self.add_cog(
            CommunityOS(self)
        )

        # Sync slash commands
        await self.tree.sync()

        await self.load_extension("modules.contributor_cog")

        print("CommunityOS loaded.")


bot = CommunityOSBot()


@bot.event
async def on_ready():

    print(
        f"Logged in as {bot.user}"
    )

    print(
        "CommunityOS is online."
    )


bot.run(DISCORD_TOKEN)