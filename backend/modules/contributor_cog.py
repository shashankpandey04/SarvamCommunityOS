from datetime import datetime, timezone

import discord

from discord.ext import commands

import database

from modules.impact_score import record_contribution

from sarvam_client import SarvamService


class ContributorCog(commands.Cog):
    """
    Tracks Discord community activity and contributor impact.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # Message Filtering
    # =================================================

    @staticmethod
    def _is_potentially_meaningful_message(
        message: discord.Message,
    ) -> bool:
        """
        Cheap local filter to avoid unnecessary Sarvam calls.
        """

        content = (
            getattr(message, "content", "")
            or ""
        ).strip()

        if not content:
            return False

        # Replies are potentially useful even if short.
        if message.reference:
            return True

        return SarvamService._should_classify(
            content
        )

    # =================================================
    # Feedback Thread Tracking
    # =================================================

    async def _track_feedback_thread_message(
        self,
        message: discord.Message,
        now: datetime,
    ) -> bool:

        if not isinstance(
            message.channel,
            discord.Thread,
        ):
            return False

        feedback_doc = database.feedback.find_one(
            {
                "thread_id": str(
                    message.channel.id
                ),
                "status": "open",
            }
        )

        if not feedback_doc:
            return False

        content = (
            message.content or ""
        ).strip()

        # Ignore empty messages.
        if not content:
            return True

        discussion_message = {
            "message_id": str(message.id),
            "user_id": str(message.author.id),
            "username": str(message.author),
            "content": content,
            "created_at": now,
        }

        database.feedback.update_one(
            {
                "_id": feedback_doc["_id"]
            },
            {
                "$push": {
                    "discussion.messages": (
                        discussion_message
                    ),
                },
                "$inc": {
                    "discussion.message_count": 1,
                },
                "$set": {
                    "updated_at": now,
                },
            },
        )

        # Tell FeedbackCog to refresh the feedback.
        feedback_cog = self.bot.get_cog(
            "FeedbackCog"
        )

        if feedback_cog:

            updated_doc = (
                database.feedback.find_one(
                    {
                        "_id": feedback_doc["_id"]
                    }
                )
            )

            if updated_doc:

                normalized = (
                    feedback_cog
                    ._coerce_feedback_document(
                        updated_doc
                    )
                )

                updated_doc.update(
                    normalized
                )

                await (
                    feedback_cog
                    ._refresh_feedback_embed(
                        updated_doc
                    )
                )

                await (
                    feedback_cog
                    ._schedule_feedback_sentiment_analysis(
                        str(
                            feedback_doc["_id"]
                        )
                    )
                )

        return True

    # =================================================
    # Contributor Tracking
    # =================================================

    async def _track_contributor(
        self,
        message: discord.Message,
        now: datetime,
    ):

        user_id = str(
            message.author.id
        )

        username = str(
            message.author
        )

        channel_name = getattr(
            message.channel,
            "name",
            "unknown",
        )

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

    # =================================================
    # Impact Classification
    # =================================================

    async def _process_impact(
        self,
        message: discord.Message,
    ):

        content = (
            message.content or ""
        ).strip()

        if not self._is_potentially_meaningful_message(
            message
        ):
            return

        classification = (
            await self.bot.sarvam.classify_message(
                content
            )
        )

        if not classification.get(
            "meaningful"
        ):
            return

        user_id = str(
            message.author.id
        )

        contribution_type = (
            classification.get("type")
        )

        contribution_types = {
            "technical_question",
            "helpful_answer",
            "feedback",
        }

        if contribution_type not in contribution_types:
            return

        record_contribution(
            discord_id=user_id,
            contribution_type=contribution_type,
        )

    # =================================================
    # Community Event
    # =================================================

    @staticmethod
    def _record_message_event(
        message: discord.Message,
        now: datetime,
    ):

        database.events.insert_one({
            "type": "message",
            "message_id": str(message.id),
            "user_id": str(message.author.id),
            "username": str(message.author),
            "channel": getattr(
                message.channel,
                "name",
                "unknown",
            ),
            "source": "discord",
            "created_at": now,
        })

    # =================================================
    # Message Listener
    # =================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ):

        # Ignore bots.
        if message.author.bot:
            return

        now = datetime.now(
            timezone.utc
        )

        # ---------------------------------------------
        # Feedback Thread
        # ---------------------------------------------

        await self._track_feedback_thread_message(
            message,
            now,
        )

        # ---------------------------------------------
        # Contributor
        # ---------------------------------------------

        await self._track_contributor(
            message,
            now,
        )

        # ---------------------------------------------
        # Impact Score
        # ---------------------------------------------

        await self._process_impact(
            message
        )

        # ---------------------------------------------
        # Community Event
        # ---------------------------------------------

        self._record_message_event(
            message,
            now,
        )


# =====================================================
# Extension Setup
# =====================================================

async def setup(
    bot: commands.Bot,
):
    await bot.add_cog(
        ContributorCog(bot)
    )