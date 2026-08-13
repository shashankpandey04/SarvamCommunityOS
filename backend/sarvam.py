import asyncio
import json
import os
import time
import json
import re

from sarvamai import SarvamAI


class SarvamService:

    def __init__(self, api_key: str):
        self.client = SarvamAI(
            api_subscription_key=api_key
        )

    # --------------------------------------------------
    # Chat
    # --------------------------------------------------

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

        response = await asyncio.to_thread(_call)

        return response.choices[0].message.content

    # --------------------------------------------------
    # Speech to Text
    # --------------------------------------------------

    async def transcribe(
        self,
        file_path: str,
    ):
        """
        Saaras v3 speech-to-text.
        """

        def _call():

            with open(file_path, "rb") as audio_file:

                return self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model="saaras:v3",
                    mode="transcribe",
                )

        return await asyncio.to_thread(_call)

    # --------------------------------------------------
    # Text to Speech
    # --------------------------------------------------

    async def speak(
        self,
        text: str,
        language: str = "hi-IN",
        speaker: str = "shubh",
    ):
        """
        Bulbul v3 text-to-speech.
        """

        def _call():
            return self.client.text_to_speech.convert(
                model="bulbul:v3",
                text=text,
                target_language_code=language,
                speaker=speaker,
            )

        return await asyncio.to_thread(_call)

    # --------------------------------------------------
    # Document Intelligence
    # --------------------------------------------------

    async def extract_document(
        self,
        file_path: str,
        schema: dict,
        language: str = "en-IN",
    ):
        """
        Sarvam Document Intelligence.
        """

        def _call():

            with open(file_path, "rb") as document:

                job = self.client.doc_ai.extract(
                    file=[
                        (
                            os.path.basename(file_path),
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

                status = self.client.doc_ai.get_status(
                    job_id=job.job_id
                )

                if status.status.lower() in terminal_states:
                    break

                time.sleep(5)

            return self.client.doc_ai.get_results(
                job_id=job.job_id
            )

        return await asyncio.to_thread(_call)

    async def analyze_query(self, question: str):
        """
        Analyze a developer question and return structured
        information for CommunityOS knowledge retrieval.
        """

        prompt = """
    You are the query analysis system for CommunityOS,
    an AI assistant for a developer community.

    Analyze the developer's question and return ONLY valid JSON.

    The JSON must contain:

    {
        "intent": "technical_question | onboarding | feedback | program_question | general",
        "topic": "one of: authentication, sdk, saaras, bulbul, chat, doc-ai, translation, hackathon, communityos, community, general",
        "keywords": ["keyword1", "keyword2"],
        "needs_human": false
    }

    Rules:

    - Choose the most relevant topic.
    - Use short, useful keywords for knowledge retrieval.
    - Do not answer the question.
    - Do not include markdown.
    - Return ONLY JSON.
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

        # ---------------------------------------------
        # Clean response
        # ---------------------------------------------

        cleaned = response.strip()

        # Handle accidental markdown fences
        if cleaned.startswith("```"):
            cleaned = re.sub(
                r"```(?:json)?",
                "",
                cleaned,
            ).strip()

            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

        # ---------------------------------------------
        # Parse JSON
        # ---------------------------------------------

        try:
            result = json.loads(cleaned)

        except json.JSONDecodeError:
            # Try extracting the first JSON object
            match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL,
            )

            if not match:
                raise ValueError(
                    "Sarvam returned invalid query analysis."
                )

            result = json.loads(
                match.group(0)
            )

        # ---------------------------------------------
        # Basic validation
        # ---------------------------------------------

        result.setdefault(
            "intent",
            "general",
        )

        result.setdefault(
            "topic",
            "general",
        )

        result.setdefault(
            "keywords",
            [],
        )

        result.setdefault(
            "needs_human",
            False,
        )

        if not isinstance(
            result["keywords"],
            list,
        ):
            result["keywords"] = []

        return result

    async def answer_question(
        self,
        question: str,
        context: str,
    ):
        """
        Generate a grounded answer using CommunityOS knowledge.
        """

        system_prompt = """
    You are CommunityOS, an AI assistant for a developer community.

    Answer the developer's question using the provided
    CommunityOS knowledge.

    Rules:
    - Use the provided knowledge as the source of truth.
    - Do not invent API capabilities, parameters, models, or
    documentation that are not present in the knowledge.
    - If the knowledge does not contain enough information,
    clearly say that you don't have enough information and
    recommend human assistance.
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