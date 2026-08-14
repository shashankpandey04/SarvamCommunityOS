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
            "communityos",
            "community",
            "general",
        }

        prompt = """
            You are the query analysis system for CommunityOS,
            an AI assistant for a developer community.

            Your job is ONLY to classify the user's question
            for knowledge retrieval.

            Return ONLY valid JSON.

            Required JSON format:

            {
                "intent": "technical_question | onboarding | feedback | program_question | general",
                "topic": "authentication | sdk | saaras | bulbul | chat | doc-ai | translation | hackathon | communityos | community | general",
                "keywords": ["keyword1", "keyword2"],
                "needs_human": false
            }

            IMPORTANT TOPIC RULES:

            1. Select a specific topic ONLY when the user's question
            clearly relates to that topic.

            2. NEVER select "communityos" simply because the question
            is being asked to CommunityOS.

            3. "communityos" is ONLY for questions specifically about
            the CommunityOS system, architecture, features,
            behavior, or implementation.

            4. "community" is for questions about the developer
            community itself, such as community participation,
            community activities, or community processes.

            5. "program_question" is an INTENT, not a topic.
            Do not use "program_question" merely because a question
            is about a product, API, model, or pricing.

            6. If the question does not clearly match any specific topic,
            use:
            
            "topic": "general"

            7. For technical questions about Sarvam products:
            - API keys/authentication → authentication
            - SDK/client usage → sdk
            - Saaras/STT → saaras
            - Bulbul/TTS → bulbul
            - Chat/105B → chat
            - Document Intelligence/Digitise/Extract → doc-ai
            - Translation/Mayura → translation

            8. Keywords must be short and useful for knowledge retrieval.
            Prefer concrete technical terms from the question.

            9. Do not answer the question.

            10. Do not include markdown.

            11. Return ONLY JSON.

            Examples:

            Question:
            "Where do I generate my Sarvam API key?"

            Output:
            {
                "intent": "technical_question",
                "topic": "authentication",
                "keywords": ["API key", "generate", "Sarvam"],
                "needs_human": false
            }

            Question:
            "What speech processing modes does Saaras v3 support?"

            Output:
            {
                "intent": "technical_question",
                "topic": "saaras",
                "keywords": ["Saaras v3", "speech processing", "modes"],
                "needs_human": false
            }

            Question:
            "Does Sarvam offer a dedicated GPU pricing calculator for developers?"

            Output:
            {
                "intent": "technical_question",
                "topic": "general",
                "keywords": ["GPU", "pricing", "calculator"],
                "needs_human": false
            }

            Question:
            "How does CommunityOS store knowledge?"

            Output:
            {
                "intent": "technical_question",
                "topic": "communityos",
                "keywords": ["CommunityOS", "knowledge", "storage"],
                "needs_human": false
            }
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

            result = json.loads(
                cleaned
            )

        except json.JSONDecodeError:

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
        # Defaults
        # ---------------------------------------------

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

        needs_human = result.get(
            "needs_human",
            False,
        )

        # ---------------------------------------------
        # Validate intent
        # ---------------------------------------------

        if intent not in allowed_intents:

            intent = "general"

        # ---------------------------------------------
        # Validate topic
        # ---------------------------------------------

        if topic not in allowed_topics:

            topic = "general"

        # ---------------------------------------------
        # Validate keywords
        # ---------------------------------------------

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

        # Remove duplicates while preserving order
        keywords = list(
            dict.fromkeys(
                keywords
            )
        )

        # Limit retrieval keywords
        keywords = keywords[:8]

        # ---------------------------------------------
        # Validate needs_human
        # ---------------------------------------------

        needs_human = bool(
            needs_human
        )

        # ---------------------------------------------
        # Final result
        # ---------------------------------------------

        return {
            "intent": intent,
            "topic": topic,
            "keywords": keywords,
            "needs_human": needs_human,
        }

    async def assess_knowledge(
        self,
        question: str,
        context: str,
    ):
        """
        Determine whether the retrieved CommunityOS
        knowledge is sufficient to answer the question.
        """

        prompt = """
            You are the knowledge sufficiency evaluator for CommunityOS.

            Determine whether the provided CommunityOS knowledge
            contains enough information to answer the user's question
            accurately and directly.

            Return ONLY valid JSON:

            {
                "sufficient": true,
                "reason": "short explanation"
            }

            Rules:

            - "sufficient" is true ONLY when the knowledge directly
            contains enough information to answer the question.
            - If the knowledge is related but does not answer the
            specific question, return false.
            - Do not use outside knowledge.
            - Do not answer the user's question.
            - Do not include markdown.
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

        try:
            result = json.loads(cleaned)

        except json.JSONDecodeError:

            match = re.search(
                r"\{.*\}",
                cleaned,
                re.DOTALL,
            )

            if not match:
                raise ValueError(
                    "Sarvam returned invalid knowledge assessment."
                )

            result = json.loads(
                match.group(0)
            )

        sufficient = result.get(
            "sufficient",
            False,
        )

        if not isinstance(sufficient, bool):
            sufficient = False

        return {
            "sufficient": sufficient,
            "reason": result.get(
                "reason",
                "",
            ),
        }

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

    async def digitise_document(
        self,
        file_path: str,
        language: str = "en-IN",
        output_format: str = "md",
    ):
        """
        Digitise an entire document into structured text
        using Sarvam Document Intelligence.
        """

        def _call():

            job = self.client.document_intelligence.create_job(
                language=language,
                output_format=output_format,
            )

            job.upload_file(
                file_path
            )

            job.start()

            status = job.wait_until_complete()

            if status.job_state.lower() not in {
                "completed",
                "partiallycompleted",
            }:
                raise RuntimeError(
                    f"Document digitisation failed: "
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

    async def text_to_speech(
        self,
        text: str,
        target_language_code: str = "en-IN",
        speaker: str = "shubh",
    ):
        response = await self.client.text_to_speech.convert(
            text=text,
            target_language_code=target_language_code,
            speaker=speaker,
            model="bulbul:v3",
        )

        return response