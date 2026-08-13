import asyncio

import discord
import database
from discord.ext import commands

import uvicorn

from api import app
from config import (
    API_HOST,
    API_PORT,
    SARVAM_API_KEY,
)
from sarvam import SarvamService


class CommunityOS(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # ---------------------------------------------
        # Sarvam
        # ---------------------------------------------

        self.bot.sarvam = SarvamService(
            SARVAM_API_KEY
        )

        # ---------------------------------------------
        # FastAPI
        # ---------------------------------------------

        self.api_task = None

    async def cog_load(self):

        self.api_task = asyncio.create_task(
            self.start_api()
        )

        print(
            f"CommunityOS API starting on "
            f"http://{API_HOST}:{API_PORT}"
        )

    async def cog_unload(self):

        if self.api_task:

            self.api_task.cancel()

    async def start_api(self):

        config = uvicorn.Config(
            app,
            host=API_HOST,
            port=API_PORT,
            log_level="info",
        )

        server = uvicorn.Server(config)

        await server.serve()

    # =================================================
    # Discord Commands
    # =================================================

    @commands.hybrid_command(
        name="ask",
        description="Ask CommunityOS a question.",
    )
    async def ask(
        self,
        ctx: commands.Context,
        *,
        question: str,
    ):

        await ctx.defer()

        answer = await self.bot.sarvam.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CommunityOS, an AI "
                        "assistant for a developer "
                        "community. Help developers "
                        "with technical and onboarding "
                        "questions. Be concise and "
                        "helpful."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ]
        )

        await ctx.followup.send(answer)

    # =================================================

    @commands.hybrid_command(
        name="feedback",
        description="Submit community feedback.",
    )
    async def feedback(
        self,
        ctx: commands.Context,
        *,
        feedback: str,
    ):

        await ctx.defer()

        classification = await self.bot.sarvam.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the following developer "
                        "community feedback into one of: "
                        "documentation, feature_request, "
                        "bug, positive, other. "
                        "Return only the category."
                    ),
                },
                {
                    "role": "user",
                    "content": feedback,
                },
            ],
            max_tokens=50,
        )

        database.feedback.insert_one({
            "user_id": str(ctx.author.id),
            "username": str(ctx.author),
            "content": feedback,
            "category": classification.strip(),
            "source": "discord",
        })

        await ctx.followup.send(
            "💡 Thanks! Your feedback has been recorded."
        )