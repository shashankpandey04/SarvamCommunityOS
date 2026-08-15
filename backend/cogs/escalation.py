import discord

from datetime import datetime, timezone

from discord.ext import commands

import database


class EscalationCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_escalation(
        self,
        ctx: commands.Context,
        sent_message,
        question: str,
        bot_answer: str,
        topic: str,
        user_id: str,
        username: str,
        now,
    ):

        guild_id = (
            str(ctx.guild.id)
            if ctx.guild
            else ""
        )

        channel_id = str(
            ctx.channel.id
        )

        # ---------------------------------------------
        # Parent bot message
        # ---------------------------------------------

        if not sent_message:
            print(
                "[ESCALATION] no bot message to thread."
            )
            return

        parent_message_id = str(
            sent_message.id
        )

        # ---------------------------------------------
        # Duplicate guard
        # ---------------------------------------------

        existing = (
            database.escalations.find_one(
                {
                    "parent_message_id":
                        parent_message_id
                }
            )
        )

        if existing:
            print(
                "[ESCALATION] duplicate skipped:"
                f" {parent_message_id}"
            )
            return

        # ---------------------------------------------
        # Create Discord thread
        # ---------------------------------------------

        thread = None

        try:

            short_question = (
                question[:60].strip()
            )

            if len(question) > 60:
                short_question += "…"

            parent_message = await ctx.channel.fetch_message(
                sent_message.id
            )

            thread = await parent_message.create_thread(
                name=f"Escalation: {short_question}",
                auto_archive_duration=1440,
            )

            print(
                "[ESCALATION] thread created:"
                f" {thread.id}"
            )

        except Exception as exc:

            print(
                "[ESCALATION] thread creation failed:"
                f" {exc}"
            )

            return

        # ---------------------------------------------
        # Save escalation
        # ---------------------------------------------

        escalation_doc = {

            "question": question,

            "user_id": user_id,

            "username": username,

            "guild_id": guild_id,

            "channel_id": channel_id,

            "parent_message_id":
                parent_message_id,

            "thread_id":
                str(thread.id),

            "topic": topic,

            "bot_answer": bot_answer,

            "status": "open",

            "messages": [],

            "created_at": now,

            "updated_at": now,

            "closed_at": None,

            "closed_by": None,
        }

        database.escalations.insert_one(
            escalation_doc
        )

        print(
            "[ESCALATION] saved:"
            f" {question[:60]}"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        EscalationCog(bot)
    )