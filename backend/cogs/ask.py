from datetime import datetime, timezone

import database

from discord.ext import commands

from knowledge import (
    search_knowledge,
    build_context,
)

from modules.impact_score import record_contribution

from utils.pagination import (
    paginate_text,
    AnswerPaginator,
)


class AskCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # /ask
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

        user_id = str(ctx.author.id)
        username = str(ctx.author)

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

            context = build_context(results)

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

                "sarvam_tools": [
                    "analyze_query",
                    "answer_question",
                ],

                "created_at": now,
            })

            # ---------------------------------------------
            # Respond
            # ---------------------------------------------

            await self._send_answer(
                ctx,
                answer,
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

        # =================================================
        # 5. Build Fallback Response
        # =================================================

        escalation_warning = (
            "\n\n---\n"
            "⚠️ **This answer may be inaccurate.**\n"
            "I couldn't find enough information in the "
            "CommunityOS knowledge base to confidently "
            "answer your question, so I've escalated it "
            "to the team. Someone from the team will "
            "respond with a confirmed answer soon."
        )

        full_answer = (
            answer + escalation_warning
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
        # 6. Save Knowledge Candidate
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
        # 7. Save Message
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

            "resolved": False,
            "escalated": True,

            "knowledge_found": False,
            "sarvam_fallback": True,

            "source": "discord",

            "created_at": now,
        })

        # =================================================
        # 8. Save Interaction
        # =================================================

        database.interactions.insert_one({
            "message_id": message_id,

            "user_id": user_id,

            "source": "discord",

            "type": intent,
            "topic": topic,

            "language": "en-IN",

            "resolved": False,
            "escalated": True,

            "knowledge_found": False,
            "sarvam_fallback": True,

            "sarvam_tools": [
                "analyze_query",
                "chat",
            ],

            "created_at": now,
        })

        # =================================================
        # 9. Respond
        # =================================================

        sent_message = await self._send_answer(
            ctx,
            full_answer,
        )

        # =================================================
        # 10. Escalate
        # =================================================

        escalation_cog = self.bot.get_cog(
            "EscalationCog"
        )

        if not escalation_cog:
            print(
                "[ESCALATION] EscalationCog is NOT loaded!"
            )
            return

        print(
            "[ESCALATION] Calling create_escalation..."
        )

        await escalation_cog.create_escalation(
            ctx=ctx,
            sent_message=sent_message,
            question=question,
            bot_answer=answer,
            topic=topic,
            user_id=user_id,
            username=username,
            now=now,
        )

    # =================================================
    # Answer Pagination
    # =================================================

    async def _send_answer(
        self,
        ctx: commands.Context,
        answer: str,
    ):

        pages = paginate_text(answer)

        if len(pages) == 1:

            return await ctx.send(
                pages[0]
            )

        view = AnswerPaginator(
            pages=pages,
            user_id=ctx.author.id,
        )

        return await ctx.send(
            pages[0],
            view=view,
        )


# =====================================================
# Extension Setup
# =====================================================

async def setup(bot: commands.Bot):

    await bot.add_cog(
        AskCog(bot)
    )