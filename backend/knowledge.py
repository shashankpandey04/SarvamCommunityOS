from datetime import datetime, timezone

from database import knowledge


# ==================================================
# Add Knowledge
# ==================================================

def add_knowledge(
    title: str,
    topic: str,
    category: str,
    content: str,
    tags: list[str] | None = None,
    source: str = "official",
    source_type: str = "manual",
    generated_by: str = "admin",
):
    """
    Add a knowledge entry to CommunityOS.
    """

    now = datetime.now(timezone.utc)

    document = {
        "title": title,
        "topic": topic,
        "category": category,
        "content": content.strip(),
        "tags": tags or [],

        # Provenance
        "source": source,
        "source_type": source_type,
        "generated_by": generated_by,

        # Time tracking
        "created_at": now,
        "updated_at": now,
    }

    result = knowledge.insert_one(document)

    return str(result.inserted_id)


# ==================================================
# Search Knowledge
# ==================================================

def search_knowledge(
    topic: str | None = None,
    keywords: list[str] | None = None,
    limit: int = 5,
):
    """
    Search CommunityOS knowledge using a two-stage
    retrieval strategy.

    Stage 1:
        Search within the detected topic.

    Stage 2:
        If topic retrieval is insufficient, perform
        broader keyword retrieval across all knowledge.

    Results are ranked using:
        - title matches
        - tag matches
        - topic matches
        - content matches

    A result must match at least two meaningful
    keywords before it can be considered relevant.
    """

    # ==================================================
    # Normalize Input
    # ==================================================

    keywords = [
        keyword.lower().strip()
        for keyword in (keywords or [])
        if keyword and keyword.strip()
    ]

    normalized_topic = (
        topic.lower().strip()
        if topic and topic.strip()
        else None
    )

    # Prevent invalid limits
    limit = max(
        1,
        min(limit, 20),
    )

    projection = {
        "_id": 0,
        "title": 1,
        "topic": 1,
        "category": 1,
        "content": 1,
        "tags": 1,
        "source": 1,
        "source_type": 1,
        "generated_by": 1,
        "created_at": 1,
        "updated_at": 1,
    }

    # ==================================================
    # Ranking Function
    # ==================================================

    def rank_results(results):

        scored = []

        for item in results:

            title = str(
                item.get(
                    "title",
                    "",
                )
            ).lower()

            content = str(
                item.get(
                    "content",
                    "",
                )
            ).lower()

            item_topic = str(
                item.get(
                    "topic",
                    "",
                )
            ).lower()

            tags = [
                str(tag).lower().strip()
                for tag in item.get(
                    "tags",
                    [],
                )
                if tag
            ]

            score = 0
            matched_keywords = 0

            # ------------------------------------------
            # Keyword Matching
            # ------------------------------------------

            for keyword in keywords:

                if not keyword:
                    continue

                keyword_score = 0

                # Exact title occurrence
                if keyword in title:
                    keyword_score += 3

                # Exact tag match
                if keyword in tags:
                    keyword_score += 3

                # Topic match
                if keyword == item_topic:
                    keyword_score += 2

                # Content occurrence
                if keyword in content:
                    keyword_score += 1

                if keyword_score > 0:

                    matched_keywords += 1

                    score += keyword_score

            # ------------------------------------------
            # No keyword overlap = irrelevant
            # ------------------------------------------

            if matched_keywords == 0:
                continue

            # ------------------------------------------
            # Topic bonus
            # ------------------------------------------

            if normalized_topic:

                if item_topic == normalized_topic:
                    score += 2

            # ------------------------------------------
            # Require meaningful keyword overlap
            #
            # One generic keyword like "Sarvam" should
            # NOT be enough to retrieve a document.
            # ------------------------------------------

            if len(keywords) >= 2:

                if matched_keywords < 2:
                    continue

            # ------------------------------------------
            # Store result
            # ------------------------------------------

            scored.append(
                {
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "item": item,
                }
            )

        # ==================================================
        # Sort
        # ==================================================

        scored.sort(
            key=lambda result: (
                result["matched_keywords"],
                result["score"],
            ),
            reverse=True,
        )

        return scored

    # ==================================================
    # Stage 1 — Topic Retrieval
    # ==================================================

    topic_results = []

    if normalized_topic:

        topic_query = {
            "topic": {
                "$regex": (
                    f"^{normalized_topic}$"
                ),
                "$options": "i",
            }
        }

        topic_results = list(
            knowledge.find(
                topic_query,
                projection,
            )
        )

    # ==================================================
    # Rank Topic Results
    # ==================================================

    scored_topic_results = rank_results(
        topic_results
    )

    # ==================================================
    # Return Strong Topic Results
    # ==================================================

    if scored_topic_results:

        best_result = scored_topic_results[0]

        # A topic result is trusted when:
        #
        # 1. At least two keywords matched
        # 2. It has a meaningful retrieval score

        if (
            best_result["matched_keywords"] >= 2
            and best_result["score"] >= 3
        ):

            return [
                result["item"]
                for result in scored_topic_results[:limit]
            ]

    # ==================================================
    # Stage 2 — Broad Keyword Retrieval
    # ==================================================

    if keywords:

        broad_results = list(
            knowledge.find(
                {},
                projection,
            )
        )

        scored_broad_results = rank_results(
            broad_results
        )

        if scored_broad_results:

            # Only return results with meaningful
            # keyword overlap.

            return [
                result["item"]
                for result in scored_broad_results[:limit]
            ]

    # ==================================================
    # Nothing Relevant Found
    # ==================================================

    return []

# ==================================================
# Build Context
# ==================================================

def build_context(
    results: list[dict],
) -> str:
    """
    Convert retrieved knowledge into context
    that can be provided to Sarvam 105B.
    """

    if not results:

        return (
            "No relevant community knowledge was found."
        )

    sections = []

    for index, item in enumerate(
        results,
        start=1,
    ):

        sections.append(
            f"""
Knowledge {index}

Title: {item.get("title", "")}
Topic: {item.get("topic", "")}
Category: {item.get("category", "")}
Source: {item.get("source", "")}

Content:
{item.get("content", "")}
""".strip()
        )

    return "\n\n---\n\n".join(
        sections
    )


# ==================================================
# Document Knowledge
# ==================================================

def add_document_knowledge(
    title: str,
    topic: str,
    category: str,
    content: str,
    document_id: str,
    tags: list[str] | None = None,
):
    """
    Add knowledge extracted from an uploaded document.
    """

    now = datetime.now(timezone.utc)

    document = {
        "title": title,
        "topic": topic,
        "category": category,
        "content": content.strip(),
        "tags": tags or [],

        "source": "document",
        "source_type": "document",
        "document_id": document_id,

        "created_at": now,
        "updated_at": now,
    }

    result = knowledge.insert_one(
        document
    )

    return str(
        result.inserted_id
    )