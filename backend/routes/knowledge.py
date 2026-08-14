from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

import database


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge"],
)


# =========================================================
# Knowledge Candidates
# =========================================================

@router.get(
    "/candidates",
    summary="Get pending knowledge candidates",
)
async def get_knowledge_candidates():

    results = database.knowledge_candidates.find(
        {
            "status": "pending",
        },
        {
            "_id": 1,
            "question": 1,
            "answer": 1,
            "topic": 1,
            "category": 1,
            "keywords": 1,
            "source": 1,
            "user_id": 1,
            "message_id": 1,
            "status": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort(
        "created_at",
        -1,
    )

    candidates = []

    for item in results:

        item["_id"] = str(
            item["_id"]
        )

        candidates.append(item)

    return candidates


# =========================================================
# Approve Knowledge Candidate
# =========================================================

@router.post(
    "/candidates/{candidate_id}/approve",
    summary="Approve a knowledge candidate",
)
async def approve_knowledge_candidate(
    candidate_id: str,
):

    try:
        object_id = ObjectId(
            candidate_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid candidate ID.",
        )

    candidate = database.knowledge_candidates.find_one(
        {
            "_id": object_id,
            "status": "pending",
        }
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail=(
                "Pending knowledge candidate "
                "not found."
            ),
        )

    now = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Create trusted knowledge
    # -----------------------------------------------------

    knowledge_document = {

        "title": candidate["question"],

        "topic": candidate.get(
            "topic",
            "general",
        ),

        "category": candidate.get(
            "category",
            "general",
        ),

        "content": candidate["answer"],

        "tags": candidate.get(
            "keywords",
            [],
        ),

        "source": "communityos_candidate",

        "source_type": "ai_fallback",

        "generated_by": "sarvam-105b",

        "created_at": now,

        "updated_at": now,

        # Audit trail
        "candidate_id": str(
            candidate["_id"]
        ),
    }

    result = database.knowledge.insert_one(
        knowledge_document
    )

    # -----------------------------------------------------
    # Mark candidate approved
    # -----------------------------------------------------

    database.knowledge_candidates.update_one(
        {
            "_id": object_id,
            "status": "pending",
        },
        {
            "$set": {
                "status": "approved",

                "reviewed_at": now,

                "updated_at": now,

                "knowledge_id": str(
                    result.inserted_id
                ),
            }
        },
    )

    return {
        "status": "approved",

        "candidate_id": candidate_id,

        "knowledge_id": str(
            result.inserted_id
        ),
    }


# =========================================================
# Reject Knowledge Candidate
# =========================================================

@router.post(
    "/candidates/{candidate_id}/reject",
    summary="Reject a knowledge candidate",
)
async def reject_knowledge_candidate(
    candidate_id: str,
):

    try:
        object_id = ObjectId(
            candidate_id
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid candidate ID.",
        )

    candidate = database.knowledge_candidates.find_one(
        {
            "_id": object_id,
            "status": "pending",
        }
    )

    if not candidate:

        raise HTTPException(
            status_code=404,
            detail=(
                "Pending knowledge candidate "
                "not found."
            ),
        )

    now = datetime.now(
        timezone.utc
    )

    database.knowledge_candidates.update_one(
        {
            "_id": object_id,
            "status": "pending",
        },
        {
            "$set": {
                "status": "rejected",

                "reviewed_at": now,

                "updated_at": now,
            }
        },
    )

    return {
        "status": "rejected",

        "candidate_id": candidate_id,
    }