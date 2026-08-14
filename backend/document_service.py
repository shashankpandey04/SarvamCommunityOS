import os
import re
import zipfile
from datetime import datetime, timezone

from database import documents, knowledge


class DocumentService:

    def __init__(self, sarvam):

        self.sarvam = sarvam

    # =================================================
    # Process PDF
    # =================================================

    async def process_pdf(
        self,
        file_path: str,
    ):
        """
        Digitise a PDF using Sarvam Document Intelligence,
        extract the generated Markdown, split it into
        knowledge sections, and store them in MongoDB.
        """

        filename = os.path.basename(file_path)

        now = datetime.now(timezone.utc)

        # ---------------------------------------------
        # Create document record
        # ---------------------------------------------

        document = {
            "filename": filename,
            "file_path": file_path,
            "status": "processing",
            "source": "upload",
            "created_at": now,
            "updated_at": now,
        }

        document_result = documents.insert_one(
            document
        )

        document_id = str(
            document_result.inserted_id
        )

        try:

            # -----------------------------------------
            # Digitise document
            # -----------------------------------------

            zip_path = await self.sarvam.digitise_document(
                file_path=file_path,
                language="en-IN",
                output_format="md",
            )

            # -----------------------------------------
            # Read generated Markdown
            # -----------------------------------------

            markdown = self._read_markdown(
                zip_path
            )

            # -----------------------------------------
            # Parse sections
            # -----------------------------------------

            sections = self._parse_sections(
                markdown
            )

            # -----------------------------------------
            # Store knowledge
            # -----------------------------------------

            knowledge_ids = []

            for section in sections:

                knowledge_document = {
                    "title": section["title"],
                    "topic": section["topic"],
                    "category": "technical_documentation",

                    "content": section["content"],

                    "tags": section["tags"],

                    "source": "document",
                    "source_type": "sarvam_doc_ai_digitise",

                    "document_id": document_id,
                    "filename": filename,

                    "generated_by": "sarvam-document-intelligence",

                    "created_at": now,
                    "updated_at": now,
                }

                result = knowledge.insert_one(
                    knowledge_document
                )

                knowledge_ids.append(
                    str(result.inserted_id)
                )

            # -----------------------------------------
            # Update document
            # -----------------------------------------

            documents.update_one(
                {
                    "_id": document_result.inserted_id
                },
                {
                    "$set": {
                        "status": "completed",
                        "knowledge_count": len(
                            knowledge_ids
                        ),
                        "knowledge_ids": knowledge_ids,
                        "updated_at": datetime.now(
                            timezone.utc
                        ),
                    }
                }
            )

            return {
                "status": "completed",
                "document_id": document_id,
                "filename": filename,
                "sections": len(sections),
                "knowledge_ids": knowledge_ids,
            }

        except Exception as error:

            # -----------------------------------------
            # Mark document as failed
            # -----------------------------------------

            documents.update_one(
                {
                    "_id": document_result.inserted_id
                },
                {
                    "$set": {
                        "status": "failed",
                        "error": str(error),
                        "updated_at": datetime.now(
                            timezone.utc
                        ),
                    }
                }
            )

            raise

    # =================================================
    # Read Markdown
    # =================================================

    def _read_markdown(
        self,
        zip_path: str,
    ) -> str:
        """
        Extract document.md from Sarvam's
        Digitise ZIP output.
        """

        if not os.path.exists(zip_path):

            raise FileNotFoundError(
                f"Digitised output not found: {zip_path}"
            )

        with zipfile.ZipFile(
            zip_path,
            "r",
        ) as archive:

            if "document.md" not in archive.namelist():

                raise ValueError(
                    "Sarvam Digitise output does not "
                    "contain document.md"
                )

            markdown = archive.read(
                "document.md"
            ).decode(
                "utf-8"
            )

        if not markdown.strip():

            raise ValueError(
                "Digitised document.md is empty."
            )

        return markdown

    # =================================================
    # Parse Markdown Sections
    # =================================================

    def _parse_sections(
        self,
        markdown: str,
    ):
        """
        Split Markdown into ## sections.
        """

        # Normalize line endings
        markdown = markdown.replace(
            "\r\n",
            "\n",
        )

        # ---------------------------------------------
        # Find ## headings
        # ---------------------------------------------

        matches = list(
            re.finditer(
                r"^##\s+(.+?)\s*$",
                markdown,
                re.MULTILINE,
            )
        )

        sections = []

        for index, match in enumerate(matches):

            title = match.group(1).strip()

            start = match.end()

            if index + 1 < len(matches):

                end = matches[
                    index + 1
                ].start()

            else:

                end = len(markdown)

            content = markdown[
                start:end
            ].strip()

            if not content:
                continue

            # Remove horizontal separators
            content = re.sub(
                r"\n---\s*\n",
                "\n",
                content,
            ).strip()

            topic = self._detect_topic(
                title,
                content,
            )

            tags = self._generate_tags(
                title,
                content,
                topic,
            )

            sections.append(
                {
                    "title": title,
                    "topic": topic,
                    "content": content,
                    "tags": tags,
                }
            )

        return sections

    # =================================================
    # Detect Topic
    # =================================================

    def _detect_topic(
        self,
        title: str,
        content: str,
    ) -> str:

        text = (
            f"{title} {content}"
        ).lower()

        if (
            "saaras" in text
            or "speech-to-text" in text
            or "speech to text" in text
            or "transcription" in text
        ):
            return "saaras"

        if (
            "bulbul" in text
            or "text-to-speech" in text
            or "text to speech" in text
        ):
            return "bulbul"

        if (
            "translation" in text
            or "translate" in text
            or "mayura" in text
        ):
            return "translation"

        if (
            "doc ai" in text
            or "document intelligence" in text
            or "digitise" in text
            or "digitization" in text
        ):
            return "doc-ai"

        return "general"

    # =================================================
    # Generate Tags
    # =================================================

    def _generate_tags(
        self,
        title: str,
        content: str,
        topic: str,
    ):

        text = (
            f"{title} {content}"
        ).lower()

        tags = set()

        # Topic
        tags.add(topic)

        # Known Sarvam technologies
        known_terms = [
            "saaras",
            "saaras-v3",
            "speech-to-text",
            "transcription",
            "transliteration",
            "codemix",

            "bulbul",
            "bulbul-v3",
            "text-to-speech",
            "tts",

            "translation",
            "sarvam-translate",
            "mayura",

            "language-detection",
            "language-code",
            "bcp47",

            "document-intelligence",
            "doc-ai",
            "digitise",
        ]

        for term in known_terms:

            if term.lower() in text:

                tags.add(term)

        return sorted(tags)