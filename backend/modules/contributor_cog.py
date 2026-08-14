from datetime import datetime, timezone

import discord
from discord.ext import commands

import database
from modules.impact_score import record_contribution
from sarvam import SarvamService


class ContributorCog(commands.Cog):
    """
    Tracks Discord community activity and contributor impact.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def _is_potentially_meaningful_message(message: discord.Message) -> bool:
        """
        Cheap local filter to avoid unnecessary Sarvam calls for
        ordinary small talk while still flagging likely technical
        questions or helpful replies.
        """

        content = (getattr(message, "content", "") or "").strip()

        if not content:
            return False

        if message.reference:
            return True

        return SarvamService._should_classify(content)

    # =================================================
    # Message Listener
    # =================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ):

        # ---------------------------------------------
        # Ignore bots
        # ---------------------------------------------

        if message.author.bot:
            return

        # ---------------------------------------------
        # Metadata
        # ---------------------------------------------

        now = datetime.now(timezone.utc)

        user_id = str(message.author.id)
        username = str(message.author)

        channel_name = getattr(
            message.channel,
            "name",
            "unknown",
        )

        message_id = str(message.id)
        message_content = (message.content or "").strip()

        # ---------------------------------------------
        # Update Contributor
        # ---------------------------------------------

        database.contributors.update_one(
            {
                "discord_id": user_id,
            },
            {
                "$set": {
                    "username": username,
                    "last_active": now,
                },

                "$setOnInsert": {
                    "discord_id": user_id,
                    "first_seen": now,
                    "impact_score": 0,
                },

                "$inc": {
                    "message_count": 1,
                },

                "$addToSet": {
                    "channels": channel_name,
                },
            },
            upsert=True,
        )

        # ---------------------------------------------
        # Impact Score
        # ---------------------------------------------

        classification = {
            "type": "casual",
            "meaningful": False,
        }

        if self._is_potentially_meaningful_message(message):
            classification = await self.bot.sarvam.classify_message(
                message_content
            )

            print(
                f"[CONTRIBUTOR] {username}: {classification}"
            )

        if classification.get("meaningful"):
            contribution_type = classification.get("type")

            if contribution_type == "technical_question":
                record_contribution(
                    discord_id=user_id,
                    contribution_type="technical_question",
                )

            elif contribution_type == "helpful_answer":
                record_contribution(
                    discord_id=user_id,
                    contribution_type="helpful_answer",
                )

            elif contribution_type == "feedback":
                record_contribution(
                    discord_id=user_id,
                    contribution_type="feedback",
                )

        # ---------------------------------------------
        # Record Community Event
        # ---------------------------------------------

        database.events.insert_one({
            "type": "message",

            "message_id": message_id,

            "user_id": user_id,

            "username": username,

            "channel": channel_name,

            "source": "discord",

            "created_at": now,
        })


async def setup(
    bot: commands.Bot,
):
    await bot.add_cog(
        ContributorCog(bot)
    )