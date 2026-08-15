from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query

import database


router = APIRouter(
    prefix="/api/feedback",
    tags=["Feedback"],
)


# =========================================================
# Helpers
# =========================================================


def parse_object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid feedback ID.",
        )


def serialize_feedback(document: dict):
    serialized = dict(document)

    serialized["_id"] = str(serialized.get("_id"))

    votes = serialized.get("votes", [])
    if not isinstance(votes, list):
        votes = []

    deduped_votes = {}

    for vote in votes:
        user_id = str(vote.get("user_id", "")).strip()
        vote_type = vote.get("vote")

        if not user_id or vote_type not in {"up", "down"}:
            continue

        deduped_votes[user_id] = {
            "user_id": user_id,
            "vote": vote_type,
            "created_at": vote.get("created_at"),
        }

    clean_votes = list(deduped_votes.values())
    upvotes = sum(1 for vote in clean_votes if vote["vote"] == "up")
    downvotes = sum(1 for vote in clean_votes if vote["vote"] == "down")

    discussion = serialized.get("discussion", {})
    if not isinstance(discussion, dict):
        discussion = {}

    messages = discussion.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    sentiment = discussion.get("sentiment", {})
    if not isinstance(sentiment, dict):
        sentiment = {}

    serialized["votes"] = clean_votes
    serialized["upvotes"] = upvotes
    serialized["downvotes"] = downvotes
    serialized["discussion"] = {
        "message_count": len(messages),
        "messages": messages,
        "sentiment": {
            "overall": sentiment.get("overall", "unknown"),
            "positive": int(sentiment.get("positive", 0) or 0),
            "neutral": int(sentiment.get("neutral", 0) or 0),
            "negative": int(sentiment.get("negative", 0) or 0),
            "summary": sentiment.get("summary"),
            "key_points": sentiment.get("key_points", []),
        },
    }

    serialized["score"] = upvotes - downvotes

    return serialized


def build_feedback_sort(sort: str):
    if sort == "oldest":
        return [("created_at", 1)]

    if sort == "most_discussed":
        return [("discussion.message_count", -1), ("updated_at", -1)]

    if sort == "relevance":
        return [("upvotes", -1), ("discussion.message_count", -1), ("updated_at", -1)]

    return [("created_at", -1)]


# =========================================================
# List Feedback
# =========================================================

@router.get(
    "",
    summary="Get community feedback",
)
async def get_feedback(
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    sort: str = Query("relevance"),
):

    query = {}

    if status:
        query["status"] = status

    results = list(
        database.feedback.find(query)
        .sort(build_feedback_sort(sort))
        .limit(limit)
    )

    return [serialize_feedback(item) for item in results]


# =========================================================
# Top Feedback
# =========================================================

@router.get(
    "/top",
    summary="Get top supported feedback suggestions",
)
async def get_top_feedback(
    limit: int = Query(10, ge=1, le=100),
    status: str = Query("open"),
):

    query = {
        "status": status,
    }

    results = list(
        database.feedback.find(query)
        .sort([
            ("upvotes", -1),
            ("discussion.message_count", -1),
            ("updated_at", -1),
        ])
        .limit(limit)
    )

    return [serialize_feedback(item) for item in results]


# =========================================================
# Feedback Detail
# =========================================================

@router.get(
    "/{feedback_id}",
    summary="Get one feedback suggestion",
)
async def get_feedback_by_id(feedback_id: str):

    object_id = parse_object_id(feedback_id)

    result = database.feedback.find_one({
        "_id": object_id,
    })

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found.",
        )

    return serialize_feedback(result)