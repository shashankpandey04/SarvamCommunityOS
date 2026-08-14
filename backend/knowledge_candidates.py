from datetime import datetime, timezone

from database import knowledge_candidates


def add_candidate(
    question: str,
    answer: str,
    topic: str,
    category: str,
    keywords: list[str] | None = None,
    user_id: str | None = None,
    message_id: str | None = None,
    source: str = "sarvam_fallback",
):
    """
    Store AI-generated knowledge as a candidate.

    Candidates are NOT trusted knowledge.
    They must be reviewed before promotion.
    """

    now = datetime.now(timezone.utc)

    document = {
        "question": question.strip(),
        "answer": answer.strip(),

        "topic": topic,
        "category": category,
        "keywords": keywords or [],

        "source": source,

        "user_id": user_id,
        "message_id": message_id,

        "status": "pending",

        "created_at": now,
        "updated_at": now,
    }

    result = knowledge_candidates.insert_one(
        document
    )

    return str(result.inserted_id)


def get_pending_candidates(
    limit: int = 20,
):
    """
    Retrieve knowledge candidates waiting
    for review.
    """

    return list(
        knowledge_candidates.find(
            {
                "status": "pending"
            },
            {
                "_id": 0,
            },
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(limit)
    )