import asyncio
import json
import os
import re
import time

from sarvamai import SarvamAI


class SarvamService:

    def __init__(self, api_key: str):

        self.client = SarvamAI(
            api_subscription_key=api_key
        )

    # =================================================
    # Internal Helpers
    # =================================================

    @staticmethod
    def _clean_json_response(response: str) -> str:

        cleaned = (response or "").strip()

        if cleaned.startswith("```"):

            cleaned = re.sub(
                r"```(?:json)?",
                "",
                cleaned,
            ).strip()

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

        return cleaned

    @classmethod
    def _parse_json_response(cls, response: str) -> dict:

        cleaned = cls._clean_json_response(
            response
        )

        try:
            return json.loads(cleaned)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL,
            )

            if not match:
                raise ValueError(
                    "Sarvam returned invalid JSON."
                )

            return json.loads(
                match.group(0)
            )

    @staticmethod
    def _empty_sentiment():

        return {
            "overall": "unknown",
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "summary": None,
            "key_points": [],
        }

    # =================================================
    # Chat
    # =================================================

    async def chat(
        self,
        messages: list,
        temperature: float = 0.2,
        top_p: float = 1,
        max_tokens: int = 2000,
    ):
        """
        Sarvam 105B conversational model.
        """

        def _call():

            return self.client.chat.completions(
                model="sarvam-105b-conversations",
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )

        response = await asyncio.to_thread(
            _call
        )

        return response.choices[0].message.content

    # =================================================
    # Speech To Text
    # =================================================

    async def transcribe(
        self,
        file_path: str,
    ):

        def _call():

            with open(
                file_path,
                "rb",
            ) as audio_file:

                return (
                    self.client
                    .speech_to_text
                    .transcribe(
                        file=audio_file,
                        model="saaras:v3",
                        mode="transcribe",
                    )
                )

        return await asyncio.to_thread(
            _call
        )

    # =================================================
    # Document Intelligence
    # =================================================

    async def extract_document(
        self,
        file_path: str,
        schema: dict,
        language: str = "en-IN",
    ):

        def _call():

            with open(
                file_path,
                "rb",
            ) as document:

                job = self.client.doc_ai.extract(
                    file=[
                        (
                            os.path.basename(
                                file_path
                            ),
                            document,
                            "application/pdf",
                        )
                    ],
                    schema=json.dumps(schema),
                    language=language,
                    output_format="json",
                )

            terminal_states = {
                "completed",
                "partially_completed",
                "failed",
                "rejected",
            }

            while True:

                status = (
                    self.client
                    .doc_ai
                    .get_status(
                        job_id=job.job_id
                    )
                )

                if (
                    status.status.lower()
                    in terminal_states
                ):
                    break

                time.sleep(5)

            return (
                self.client
                .doc_ai
                .get_results(
                    job_id=job.job_id
                )
            )

        return await asyncio.to_thread(
            _call
        )

    # =================================================
    # Message Classification
    # =================================================

    async def classify_message(
        self,
        message: str,
    ):

        if not isinstance(
            message,
            str,
        ):
            return {
                "type": "casual",
                "meaningful": False,
            }

        message = message.strip()

        if not message:

            return {
                "type": "casual",
                "meaningful": False,
            }

        prompt = """
You are the message classifier for CommunityOS.

Classify the provided Discord community message.
Do not answer the message.
Do not provide explanations.

Return ONLY valid JSON:

{
    "type": "technical_question | helpful_answer | casual | feedback | other",
    "meaningful": true
}

Rules:
- technical_question = genuine developer or community question.
- helpful_answer = useful reply, explanation, or guidance.
- casual = greetings, small talk, jokes, thanks, or trivial chatter.
- feedback = feature feedback, bug report, suggestion, or product experience feedback.
- other = anything else.
- meaningful is true only when the message has clear community value.

Return ONLY JSON.
"""

        try:

            response = await self.chat(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                temperature=0,
                max_tokens=200,
            )

            result = self._parse_json_response(
                response
            )

        except Exception:

            return {
                "type": "casual",
                "meaningful": False,
            }

        allowed_types = {
            "technical_question",
            "helpful_answer",
            "casual",
            "feedback",
            "other",
        }

        message_type = result.get(
            "type",
            "casual",
        )

        if message_type not in allowed_types:
            message_type = "casual"

        return {
            "type": message_type,
            "meaningful": bool(
                result.get(
                    "meaningful",
                    False,
                )
            ),
        }

    # =================================================
    # Local Message Filter
    # =================================================

    @staticmethod
    def _should_classify(
        message: str,
    ) -> bool:

        if not isinstance(
            message,
            str,
        ):
            return False

        cleaned = re.sub(
            r"<@!?(\d+)>|<@&(\d+)>|<#(\d+)>|https?://\S+",
            " ",
            message,
            flags=re.IGNORECASE,
        )

        cleaned = " ".join(
            cleaned.split()
        )

        if not cleaned:
            return False

        lowered = cleaned.lower()

        casual_phrases = {
            "anyone there",
            "hey everyone",
            "good morning",
            "good night",
            "lol",
            "haha",
            "what's up",
            "what is up",
            "thanks",
            "thank you",
            "okay",
            "cool",
            "bro",
            "hello",
            "hi there",
            "hey",
            "yo",
            "sup",
            "good evening",
        }

        if (
            lowered in casual_phrases
            or lowered.startswith(
                (
                    "hey",
                    "hi ",
                    "hello",
                    "thanks",
                    "thank you",
                    "lol",
                    "haha",
                    "okay",
                    "cool",
                    "bro",
                    "yo",
                    "sup",
                )
            )
        ):
            return False

        question_like = "?" in message

        technical_indicators = (
            "how ",
            "why ",
            "what ",
            "when ",
            "where ",
            "which ",
            "can ",
            "does ",
            "is ",
            "are ",
            "help",
            "api",
            "auth",
            "token",
            "sdk",
            "saaras",
            "bulbul",
            "communityos",
            "request",
            "response",
            "error",
            "401",
            "500",
            "login",
            "generate",
            "how to",
            "why is",
            "how does",
            "what is",
            "can someone",
            "does sarvam",
        )

        if question_like:

            return (
                len(cleaned.split()) >= 3
                and not any(
                    phrase in lowered
                    for phrase in casual_phrases
                )
            )

        return any(
            indicator in lowered
            for indicator in technical_indicators
        )

    # =================================================
    # Query Analysis
    # =================================================

    async def analyze_query(
        self,
        question: str,
    ):

        allowed_intents = {
            "technical_question",
            "onboarding",
            "feedback",
            "program_question",
            "general",
        }

        allowed_topics = {
            "authentication",
            "sdk",
            "saaras",
            "bulbul",
            "chat",
            "doc-ai",
            "translation",
            "hackathon",
            "sarvamai",
            "community",
            "general",
        }

        prompt = """
You are the query analysis system for SarvamAI,
an AI assistant for a developer community.

Your job is ONLY to classify the user's question
for knowledge retrieval.

Return ONLY valid JSON:

{
    "intent": "technical_question | onboarding | feedback | program_question | general",
    "topic": "authentication | sdk | saaras | bulbul | chat | doc-ai | translation | hackathon | sarvamai | community | general",
    "keywords": ["keyword1", "keyword2"],
    "needs_human": false
}

Rules:

1. Select a specific topic only when clearly relevant.
2. Never select "sarvamai" simply because the question is being asked to SarvamAI.
3. "sarvamai" is only for questions specifically about SarvamAI.
4. "community" is for questions about the developer community.
5. "program_question" is an intent, not a topic.
6. Use "general" when no specific topic matches.
7. API keys/authentication → authentication.
8. SDK/client usage → sdk.
9. Saaras/STT → saaras.
10. Bulbul/TTS → bulbul.
11. Chat/105B → chat.
12. Document Intelligence → doc-ai.
13. Translation/Mayura → translation.
14. Keywords must be short and useful.
15. Do not answer the question.
16. Return ONLY JSON.
"""

        response = await self.chat(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0,
            max_tokens=300,
        )

        result = self._parse_json_response(
            response
        )

        intent = result.get(
            "intent",
            "general",
        )

        topic = result.get(
            "topic",
            "general",
        )

        keywords = result.get(
            "keywords",
            [],
        )

        if intent not in allowed_intents:
            intent = "general"

        if topic not in allowed_topics:
            topic = "general"

        if not isinstance(
            keywords,
            list,
        ):
            keywords = []

        keywords = [
            str(keyword).strip()
            for keyword in keywords
            if str(keyword).strip()
        ]

        keywords = list(
            dict.fromkeys(keywords)
        )[:8]

        return {
            "intent": intent,
            "topic": topic,
            "keywords": keywords,
            "needs_human": bool(
                result.get(
                    "needs_human",
                    False,
                )
            ),
        }

    # =================================================
    # Feedback Sentiment
    # =================================================

    async def analyze_feedback_discussion(
        self,
        suggestion: str,
        discussion_messages: list[dict],
    ):

        if not discussion_messages:
            return self._empty_sentiment()

        condensed_messages = []

        for item in discussion_messages[-30:]:

            username = (
                str(
                    item.get(
                        "username",
                        "user",
                    )
                ).strip()
                or "user"
            )

            content = (
                str(
                    item.get(
                        "content",
                        "",
                    )
                ).strip()
            )

            if not content:
                continue

            condensed_messages.append(
                f"{username}: {content}"
            )

        if not condensed_messages:
            return self._empty_sentiment()

        prompt = """
You are an analyst for a developer community team.

Analyze community discussion around one feedback suggestion.

Return ONLY valid JSON:

{
    "overall": "positive | neutral | negative | mixed | unknown",
    "positive": 0,
    "neutral": 0,
    "negative": 0,
    "summary": "short summary",
    "key_points": ["point 1", "point 2"]
}

Rules:
- Percentages must be integers from 0 to 100.
- positive + neutral + negative must equal 100.
- Keep summary concise and factual.
- key_points should highlight recurring support, concerns, or objections.
- Return only JSON.
"""

        try:

            response = await self.chat(
                messages=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Suggestion:\n"
                            f"{suggestion}\n\n"
                            "Discussion:\n"
                            + "\n".join(
                                condensed_messages
                            )
                        ),
                    },
                ],
                temperature=0,
                max_tokens=500,
            )

            result = self._parse_json_response(
                response
            )

        except Exception:

            return self._empty_sentiment()

        allowed_overall = {
            "positive",
            "neutral",
            "negative",
            "mixed",
            "unknown",
        }

        overall = str(
            result.get(
                "overall",
                "unknown",
            )
        ).strip().lower()

        if overall not in allowed_overall:
            overall = "unknown"

        def to_percent(value):

            try:
                return max(
                    0,
                    min(
                        100,
                        int(value),
                    ),
                )
            except Exception:
                return 0

        positive = to_percent(
            result.get(
                "positive",
                0,
            )
        )

        neutral = to_percent(
            result.get(
                "neutral",
                0,
            )
        )

        negative = to_percent(
            result.get(
                "negative",
                0,
            )
        )

        total = (
            positive
            + neutral
            + negative
        )

        if total != 100:

            if total <= 0:

                positive = 0
                neutral = 100
                negative = 0

            else:

                positive = round(
                    positive / total * 100
                )

                neutral = round(
                    neutral / total * 100
                )

                negative = max(
                    0,
                    100
                    - positive
                    - neutral,
                )

        summary = result.get(
            "summary"
        )

        if summary is not None:
            summary = (
                str(summary).strip()
                or None
            )

        key_points = result.get(
            "key_points",
            [],
        )

        if not isinstance(
            key_points,
            list,
        ):
            key_points = []

        key_points = [
            str(point).strip()
            for point in key_points
            if str(point).strip()
        ][:5]

        return {
            "overall": overall,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "summary": summary,
            "key_points": key_points,
        }

    # =================================================
    # Knowledge Assessment
    # =================================================

    async def assess_knowledge(
        self,
        question: str,
        context: str,
    ):

        prompt = """
You are the knowledge sufficiency evaluator for SarvamAI.

Determine whether the provided knowledge contains
enough information to answer the user's question accurately.

Return ONLY valid JSON:

{
    "sufficient": true,
    "reason": "short explanation"
}

Rules:
- true only when the knowledge directly answers the question.
- Related but insufficient knowledge → false.
- Do not use outside knowledge.
- Do not answer the question.
- Return ONLY JSON.

Community knowledge:

""" + context

        response = await self.chat(
            messages=[
                {
                    "role": "system",
                    "content": prompt,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0,
            max_tokens=200,
        )

        result = self._parse_json_response(
            response
        )

        sufficient = result.get(
            "sufficient",
            False,
        )

        if not isinstance(
            sufficient,
            bool,
        ):
            sufficient = False

        return {
            "sufficient": sufficient,
            "reason": result.get(
                "reason",
                "",
            ),
        }

    # =================================================
    # Grounded Answer
    # =================================================

    async def answer_question(
        self,
        question: str,
        context: str,
    ):

        system_prompt = """
You are SarvamAI, an AI assistant for a developer community.

Answer the developer's question using the provided
SarvamAI knowledge.

Rules:
- Use the provided knowledge as the source of truth.
- Do not invent API capabilities, parameters, models,
  or documentation.
- If the knowledge is insufficient, clearly say so.
- Be concise and practical.
- Include code examples when the knowledge provides them.
- Do not mention the internal retrieval process.

Community knowledge:

""" + context

        return await self.chat(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
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
    # Document Digitisation
    # =================================================

    async def digitise_document(
        self,
        file_path: str,
        language: str = "en-IN",
        output_format: str = "md",
    ):

        def _call():

            job = (
                self.client
                .document_intelligence
                .create_job(
                    language=language,
                    output_format=output_format,
                )
            )

            job.upload_file(
                file_path
            )

            job.start()

            status = (
                job.wait_until_complete()
            )

            if (
                status.job_state.lower()
                not in {
                    "completed",
                    "partiallycompleted",
                }
            ):
                raise RuntimeError(
                    "Document digitisation failed: "
                    f"{status.job_state}"
                )

            output_path = (
                f"{file_path}.digitised.zip"
            )

            job.download_output(
                output_path
            )

            return output_path

        return await asyncio.to_thread(
            _call
        )

    # =================================================
    # Text To Speech
    # =================================================

    async def text_to_speech(
        self,
        text: str,
        target_language_code: str = "en-IN",
        speaker: str = "shubh",
    ):

        def _call():

            return (
                self.client
                .text_to_speech
                .convert(
                    text=text,
                    target_language_code=(
                        target_language_code
                    ),
                    speaker=speaker,
                    model="bulbul:v3",
                )
            )

        return await asyncio.to_thread(
            _call
        )