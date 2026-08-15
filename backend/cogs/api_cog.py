import asyncio

import uvicorn
from discord.ext import commands

from api import app
from config import API_HOST, API_PORT


class APICog(commands.Cog):
    """
    Starts the FastAPI/uvicorn server as a background
    task inside the Discord bot process.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_task: asyncio.Task | None = None

    async def cog_load(self):
        self.api_task = asyncio.create_task(
            self._serve()
        )
        print(
            f"[API] starting on "
            f"http://{API_HOST}:{API_PORT}"
        )

    async def cog_unload(self):
        if self.api_task and not self.api_task.done():
            self.api_task.cancel()

    async def _serve(self):
        config = uvicorn.Config(
            app,
            host=API_HOST,
            port=API_PORT,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()


async def setup(bot: commands.Bot):
    await bot.add_cog(
        APICog(bot)
    )