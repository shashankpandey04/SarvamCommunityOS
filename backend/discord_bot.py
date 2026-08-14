import asyncio

import discord
import database

from datetime import datetime, timezone
from discord.ext import commands

from modules.impact_score import record_contribution

import uvicorn

from api import app
from config import (
    API_HOST,
    API_PORT,
    SARVAM_API_KEY,
)
from knowledge import (
    search_knowledge,
    build_context,
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

        # =================================================
        # Request Metadata
        # =================================================

        now = datetime.now(timezone.utc)

        user_id = str(
            ctx.author.id
        )

        username = str(
            ctx.author
        )

        message_id = str(
            getattr(
                ctx.message,
                "id",
                "",
            )
        )

        channel_name = getattr(
            ctx.channel,
            "name",
            "unknown",
        )

        # =================================================
        # 1. Analyze Question
        # =================================================

        analysis = await self.bot.sarvam.analyze_query(
            question
        )

        intent = analysis.get(
            "intent",
            "general",
        )

        topic = analysis.get(
            "topic",
            "general",
        )

        keywords = analysis.get(
            "keywords",
            [],
        )

        needs_human = analysis.get(
            "needs_human",
            False,
        )

        # =================================================
        # 2. Search CommunityOS Knowledge
        # =================================================

        results = search_knowledge(
            topic=topic,
            keywords=keywords,
            limit=5,
        )

        # =================================================
        # 3. Knowledge Found
        # =================================================

        if results:

            context = build_context(
                results
            )

            answer = await self.bot.sarvam.answer_question(
                question=question,
                context=context,
            )

            # ---------------------------------------------
            # Contributor Impact
            # ---------------------------------------------

            if intent == "technical_question":
                record_contribution(
                    discord_id=user_id,
                    contribution_type="technical_question",
                )

            # ---------------------------------------------
            # Save Message
            # ---------------------------------------------

            database.messages.insert_one({

                "discord_message_id": message_id,

                "user_id": user_id,
                "username": username,

                "channel": channel_name,

                "content": question,

                "language": "en-IN",

                "intent": intent,
                "topic": topic,
                "keywords": keywords,

                "resolved": True,
                "escalated": needs_human,

                "knowledge_found": True,
                "sarvam_fallback": False,

                "source": "discord",

                "created_at": now,
            })

            # ---------------------------------------------
            # Save Interaction
            # ---------------------------------------------

            database.interactions.insert_one({

                "message_id": message_id,

                "user_id": user_id,

                "source": "discord",

                "type": intent,
                "topic": topic,

                "language": "en-IN",

                "resolved": True,
                "escalated": needs_human,

                "knowledge_found": True,
                "sarvam_fallback": False,

                # Correct:
                # We analyzed the question and then
                # answered using retrieved knowledge.
                "sarvam_tools": [
                    "analyze_query",
                    "answer_question",
                ],

                "created_at": now,
            })

            # ---------------------------------------------
            # Respond
            # ---------------------------------------------

            await ctx.send(
                answer
            )

            return

        # =================================================
        # 4. Knowledge NOT Found
        # =================================================

        answer = await self.bot.sarvam.chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are CommunityOS, an AI "
                        "assistant for a developer community. "
                        "Answer the user's question helpfully. "
                        "If you are uncertain, clearly say so. "
                        "Do not pretend that uncertain information "
                        "is official CommunityOS knowledge."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        # ---------------------------------------------
        # Contributor Impact
        # ---------------------------------------------

        if intent == "technical_question":
            record_contribution(
                discord_id=user_id,
                contribution_type="technical_question",
            )


        # =================================================
        # 5. Save Knowledge Candidate
        # =================================================

        database.knowledge_candidates.insert_one({

            "question": question,

            "answer": answer,

            "topic": topic,

            "category": intent,

            "keywords": keywords,

            "source": "sarvam_fallback",

            "user_id": user_id,

            "message_id": message_id,

            "status": "pending",

            "created_at": now,

            "updated_at": now,
        })

        # =================================================
        # 6. Save Message
        # =================================================

        database.messages.insert_one({

            "discord_message_id": message_id,

            "user_id": user_id,
            "username": username,

            "channel": channel_name,

            "content": question,

            "language": "en-IN",

            "intent": intent,
            "topic": topic,
            "keywords": keywords,

            "resolved": True,
            "escalated": needs_human,

            "knowledge_found": False,
            "sarvam_fallback": True,

            "source": "discord",

            "created_at": now,
        })

        # =================================================
        # 7. Save Interaction
        # =================================================

        database.interactions.insert_one({

            "message_id": message_id,

            "user_id": user_id,

            "source": "discord",

            "type": intent,
            "topic": topic,

            "language": "en-IN",

            "resolved": True,
            "escalated": needs_human,

            "knowledge_found": False,
            "sarvam_fallback": True,

            # Fallback path:
            "sarvam_tools": [
                "analyze_query",
                "chat",
            ],

            "created_at": now,
        })

        # =================================================
        # 8. Respond to User
        # =================================================

        await ctx.send(
            answer
        )

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
            "created_at": datetime.now(timezone.utc),
        })

        await ctx.send(
            "💡 Thanks! Your feedback has been recorded."
        )