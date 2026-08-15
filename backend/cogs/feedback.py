import asyncio
from datetime import datetime, timezone

import discord
import database

from bson import ObjectId
from discord.ext import commands

from config import FEEDBACK_CHANNEL_ID


class FeedbackCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.feedback_analysis_tasks: dict[
            str, asyncio.Task
        ] = {}

    # =================================================
    # Helpers
    # =================================================

    @staticmethod
    def _feedback_sentiment_default():
        return {
            "overall": "unknown",
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "summary": None,
            "key_points": [],
        }

    @staticmethod
    def _emoji_to_vote(emoji: str):
        if emoji == "👍":
            return "up"

        if emoji == "👎":
            return "down"

        return None

    @staticmethod
    def _coerce_feedback_document(document: dict):
        votes = document.get("votes", [])

        if not isinstance(votes, list):
            votes = []

        deduped_votes = {}

        for vote in votes:
            user_id = str(
                vote.get("user_id", "")
            ).strip()

            vote_type = vote.get("vote")

            if not user_id or vote_type not in {"up", "down"}:
                continue

            deduped_votes[user_id] = {
                "user_id": user_id,
                "vote": vote_type,
                "created_at": vote.get("created_at"),
            }

        clean_votes = list(deduped_votes.values())

        upvotes = sum(
            1 for vote in clean_votes
            if vote["vote"] == "up"
        )

        downvotes = sum(
            1 for vote in clean_votes
            if vote["vote"] == "down"
        )

        discussion = document.get("discussion", {})

        if not isinstance(discussion, dict):
            discussion = {}

        messages = discussion.get("messages", [])

        if not isinstance(messages, list):
            messages = []

        sentiment = discussion.get("sentiment", {})

        if not isinstance(sentiment, dict):
            sentiment = {}

        return {
            "votes": clean_votes,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "discussion": {
                "message_count": len(messages),
                "messages": messages,
                "sentiment": {
                    "overall": sentiment.get(
                        "overall",
                        "unknown",
                    ),
                    "positive": int(
                        sentiment.get("positive", 0) or 0
                    ),
                    "neutral": int(
                        sentiment.get("neutral", 0) or 0
                    ),
                    "negative": int(
                        sentiment.get("negative", 0) or 0
                    ),
                    "summary": sentiment.get("summary"),
                    "key_points": sentiment.get(
                        "key_points",
                        [],
                    ),
                },
            },
        }

    def _build_feedback_embed(self, feedback_doc: dict):
        sentiment = (
            feedback_doc
            .get("discussion", {})
            .get("sentiment", {})
            .get("overall", "unknown")
        )

        summary = (
            feedback_doc
            .get("discussion", {})
            .get("sentiment", {})
            .get("summary")
        )

        embed = discord.Embed(
            title="Community Feedback",
            description=feedback_doc.get(
                "suggestion",
                "",
            ),
            color=discord.Color.blurple(),
            timestamp=feedback_doc.get("created_at"),
        )

        embed.add_field(
            name="Submitted By",
            value=feedback_doc.get(
                "author_name",
                "Unknown",
            ),
            inline=False,
        )

        embed.add_field(
            name="Votes",
            value=(
                f"👍 {feedback_doc.get('upvotes', 0)}\n"
                f"👎 {feedback_doc.get('downvotes', 0)}"
            ),
            inline=True,
        )

        embed.add_field(
            name="Discussion",
            value=(
                f"{feedback_doc.get('discussion', {})}"
                ".get('message_count', 0)} messages"
            ),
            inline=True,
        )

        embed.add_field(
            name="Sentiment",
            value=str(sentiment).capitalize(),
            inline=True,
        )

        if summary:
            embed.add_field(
                name="Summary",
                value=str(summary)[:1024],
                inline=False,
            )

        embed.set_footer(
            text=f"Feedback ID: {feedback_doc.get('_id')}"
        )

        return embed

    async def _resolve_feedback_channel(self):
        raw_channel_id = (
            FEEDBACK_CHANNEL_ID or ""
        ).strip()

        if not raw_channel_id:
            return None

        try:
            channel_id = int(raw_channel_id)
        except ValueError:
            return None

        channel = self.bot.get_channel(channel_id)

        if channel:
            return channel

        try:
            return await self.bot.fetch_channel(channel_id)
        except Exception:
            return None

    async def _fetch_discord_message(
        self,
        channel_id: str,
        message_id: str,
    ):
        if not channel_id or not message_id:
            return None

        try:
            channel_id = int(channel_id)
            message_id = int(message_id)
        except (TypeError, ValueError):
            return None

        channel = self.bot.get_channel(channel_id)

        if not channel:
            try:
                channel = await self.bot.fetch_channel(
                    channel_id
                )
            except Exception:
                return None

        if not hasattr(channel, "fetch_message"):
            return None

        try:
            return await channel.fetch_message(message_id)
        except Exception:
            return None

    async def _refresh_feedback_embed(
        self,
        feedback_doc: dict,
    ):
        message = await self._fetch_discord_message(
            feedback_doc.get("channel_id", ""),
            feedback_doc.get("message_id", ""),
        )

        if not message:
            return

        embed = self._build_feedback_embed(
            feedback_doc
        )

        try:
            await message.edit(embed=embed)
        except Exception:
            return

    # =================================================
    # Sentiment Analysis
    # =================================================

    async def _schedule_feedback_sentiment_analysis(
        self,
        feedback_id: str,
    ):
        existing = self.feedback_analysis_tasks.get(
            feedback_id
        )

        if existing and not existing.done():
            existing.cancel()

        task = asyncio.create_task(
            self._run_feedback_sentiment_analysis(
                feedback_id
            )
        )

        self.feedback_analysis_tasks[
            feedback_id
        ] = task

    async def _run_feedback_sentiment_analysis(
        self,
        feedback_id: str,
    ):
        try:
            await asyncio.sleep(10)

            try:
                feedback_object_id = ObjectId(
                    feedback_id
                )
            except Exception:
                return

            feedback_doc = database.feedback.find_one(
                {"_id": feedback_object_id}
            )

            if not feedback_doc:
                return

            discussion = feedback_doc.get(
                "discussion",
                {},
            )

            messages = discussion.get(
                "messages",
                [],
            )

            if not isinstance(messages, list) or not messages:
                return

            sentiment = (
                await self.bot.sarvam
                .analyze_feedback_discussion(
                    suggestion=feedback_doc.get(
                        "suggestion",
                        "",
                    ),
                    discussion_messages=messages,
                )
            )

            existing_sentiment = (
                feedback_doc
                .get("discussion", {})
                .get("sentiment", {})
            )

            unknown_result = (
                sentiment.get("overall") == "unknown"
                and not sentiment.get("summary")
                and not sentiment.get("key_points")
            )

            if (
                unknown_result
                and existing_sentiment.get(
                    "overall"
                ) not in {None, "unknown"}
            ):
                sentiment = existing_sentiment

            now = datetime.now(timezone.utc)

            database.feedback.update_one(
                {"_id": feedback_object_id},
                {
                    "$set": {
                        "discussion.sentiment": sentiment,
                        "updated_at": now,
                    }
                },
            )

            updated_doc = database.feedback.find_one(
                {"_id": feedback_object_id}
            )

            if updated_doc:
                normalized = (
                    self._coerce_feedback_document(
                        updated_doc
                    )
                )

                updated_doc.update(normalized)

                await self._refresh_feedback_embed(
                    updated_doc
                )

        except asyncio.CancelledError:
            return

        except Exception as exc:
            print(
                f"[FEEDBACK] sentiment analysis failed: "
                f"{exc}"
            )

    # =================================================
    # Vote Sync
    # =================================================

    async def _sync_feedback_vote(
        self,
        feedback_doc: dict,
        user_id: str,
        vote_type: str,
        remove_vote: bool = False,
    ):
        now = datetime.now(timezone.utc)

        normalized = self._coerce_feedback_document(
            feedback_doc
        )

        votes = normalized["votes"]

        if remove_vote:
            votes = [
                vote
                for vote in votes
                if vote.get("user_id") != user_id
            ]

        else:
            replaced = False

            for vote in votes:
                if vote.get("user_id") == user_id:
                    vote["vote"] = vote_type
                    vote["created_at"] = now
                    replaced = True
                    break

            if not replaced:
                votes.append(
                    {
                        "user_id": user_id,
                        "vote": vote_type,
                        "created_at": now,
                    }
                )

        deduped = {}

        for vote in votes:
            uid = vote.get("user_id")

            if uid:
                deduped[uid] = vote

        clean_votes = list(deduped.values())

        upvotes = sum(
            1
            for vote in clean_votes
            if vote.get("vote") == "up"
        )

        downvotes = sum(
            1
            for vote in clean_votes
            if vote.get("vote") == "down"
        )

        database.feedback.update_one(
            {"_id": feedback_doc["_id"]},
            {
                "$set": {
                    "votes": clean_votes,
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "updated_at": now,
                }
            },
        )

        updated = database.feedback.find_one(
            {"_id": feedback_doc["_id"]}
        )

        if not updated:
            return None

        normalized_updated = (
            self._coerce_feedback_document(updated)
        )

        updated.update(normalized_updated)

        return updated

    # =================================================
    # /feedback
    # =================================================

    @commands.hybrid_command(
        name="feedback",
        description="Submit community feedback.",
    )
    async def feedback(
        self,
        ctx: commands.Context,
        *,
        suggestion: str,
    ):
        await ctx.defer()

        suggestion = (suggestion or "").strip()

        if len(suggestion) < 8:
            await ctx.send(
                "Please provide a more detailed suggestion."
            )
            return

        feedback_channel = (
            await self._resolve_feedback_channel()
        )

        if not feedback_channel:
            await ctx.send(
                "Feedback channel is not configured "
                "or not accessible."
            )
            return

        now = datetime.now(timezone.utc)

        feedback_doc = {
            "suggestion": suggestion,
            "author_id": str(ctx.author.id),
            "author_name": str(ctx.author),
            "channel_id": str(feedback_channel.id),
            "votes": [],
            "upvotes": 0,
            "downvotes": 0,
            "discussion": {
                "message_count": 0,
                "messages": [],
                "sentiment": (
                    self._feedback_sentiment_default()
                ),
            },
            "status": "open",
            "source": "discord",
            "created_at": now,
            "updated_at": now,
        }

        insert_result = database.feedback.insert_one(
            feedback_doc
        )

        feedback_doc["_id"] = (
            insert_result.inserted_id
        )

        embed = self._build_feedback_embed(
            feedback_doc
        )

        try:
            feedback_message = (
                await feedback_channel.send(
                    embed=embed
                )
            )

        except Exception:
            database.feedback.delete_one(
                {"_id": feedback_doc["_id"]}
            )

            await ctx.send(
                "Failed to post feedback in the "
                "configured channel."
            )

            return

        thread = None

        try:
            thread_title = suggestion[:70]

            thread = (
                await feedback_message.create_thread(
                    name=f"Feedback: {thread_title}",
                    auto_archive_duration=1440,
                )
            )

        except Exception as exc:
            print(
                f"[FEEDBACK] thread creation failed: {exc}"
            )

        try:
            await feedback_message.add_reaction("👍")
            await feedback_message.add_reaction("👎")

        except Exception as exc:
            print(
                f"[FEEDBACK] adding reactions failed: {exc}"
            )

        database.feedback.update_one(
            {"_id": feedback_doc["_id"]},
            {
                "$set": {
                    "message_id": str(
                        feedback_message.id
                    ),
                    "thread_id": (
                        str(thread.id)
                        if thread
                        else ""
                    ),
                    "updated_at": datetime.now(
                        timezone.utc
                    ),
                }
            },
        )

        await ctx.send(
            "Thanks. Your feedback has been submitted "
            "and discussion thread is ready."
        )

    # =================================================
    # Reactions
    # =================================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (
            self.bot.user
            and payload.user_id == self.bot.user.id
        ):
            return

        if payload.member and payload.member.bot:
            return

        vote_type = self._emoji_to_vote(
            str(payload.emoji)
        )

        if not vote_type:
            return

        feedback_doc = database.feedback.find_one(
            {
                "message_id": str(
                    payload.message_id
                )
            }
        )

        if not feedback_doc:
            return

        updated = await self._sync_feedback_vote(
            feedback_doc=feedback_doc,
            user_id=str(payload.user_id),
            vote_type=vote_type,
            remove_vote=False,
        )

        if not updated:
            return

        message = await self._fetch_discord_message(
            updated.get("channel_id", ""),
            updated.get("message_id", ""),
        )

        opposite = (
            "👎"
            if vote_type == "up"
            else "👍"
        )

        if message:
            try:
                user = self.bot.get_user(
                    payload.user_id
                )

                if not user:
                    user = await self.bot.fetch_user(
                        payload.user_id
                    )

                await message.remove_reaction(
                    opposite,
                    user,
                )

            except Exception:
                pass

        await self._refresh_feedback_embed(
            updated
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if (
            self.bot.user
            and payload.user_id == self.bot.user.id
        ):
            return

        user = self.bot.get_user(
            payload.user_id
        )

        if user is None:
            try:
                user = await self.bot.fetch_user(
                    payload.user_id
                )
            except Exception:
                user = None

        if user and getattr(user, "bot", False):
            return

        vote_type = self._emoji_to_vote(
            str(payload.emoji)
        )

        if not vote_type:
            return

        feedback_doc = database.feedback.find_one(
            {
                "message_id": str(
                    payload.message_id
                )
            }
        )

        if not feedback_doc:
            return

        normalized = (
            self._coerce_feedback_document(
                feedback_doc
            )
        )

        existing_vote = None

        for vote in normalized["votes"]:
            if vote.get("user_id") == str(
                payload.user_id
            ):
                existing_vote = vote.get("vote")
                break

        if existing_vote != vote_type:
            return

        updated = await self._sync_feedback_vote(
            feedback_doc=feedback_doc,
            user_id=str(payload.user_id),
            vote_type=vote_type,
            remove_vote=True,
        )

        if updated:
            await self._refresh_feedback_embed(
                updated
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        FeedbackCog(bot)
    )