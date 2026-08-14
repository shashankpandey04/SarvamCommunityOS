from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

import database


router = APIRouter(
    prefix="/api/knowledge",
    tags=["Knowledge"],
)


# =========================================================
# Request Models
# =========================================================


class ApproveKnowledgeRequest(BaseModel):
    answer: str | None = None


class UpdateKnowledgeRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    topic: str | None = None
    category: str | None = None
    tags: list[str] | None = None


class MergeCandidatesRequest(BaseModel):
    candidate_ids: list[str] = Field(
        min_length=2,
        description="IDs of pending candidates to merge",
    )


# =========================================================
# Helpers
# =========================================================


def parse_object_id(value: str):
    """
    Convert a string into MongoDB ObjectId.
    """

    try:
        return ObjectId(value)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid knowledge ID.",
        )


def serialize_document(document: dict):
    """
    Convert MongoDB ObjectId into a JSON-safe string.
    """

    if "_id" in document:
        document["_id"] = str(
            document["_id"]
        )

    return document


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
            "occurrences": 1,
            "question_variants": 1,
            "merged_candidate_ids": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort(
        "created_at",
        -1,
    )

    candidates = []

    for item in results:

        item = serialize_document(item)

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
    request: ApproveKnowledgeRequest,
):

    object_id = parse_object_id(
        candidate_id
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
    # Use edited answer if supplied
    # -----------------------------------------------------

    final_answer = (
        request.answer.strip()
        if request.answer
        and request.answer.strip()
        else candidate["answer"]
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

        "content": final_answer,

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

        # Useful when the same question
        # appeared multiple times.
        "occurrences": candidate.get(
            "occurrences",
            1,
        ),

        "question_variants": candidate.get(
            "question_variants",
            [
                candidate["question"]
            ],
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

    object_id = parse_object_id(
        candidate_id
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


# =========================================================
# Merge Pending Knowledge Candidates
# =========================================================


@router.post(
    "/candidates/merge",
    summary="Merge duplicate pending knowledge candidates",
)
async def merge_knowledge_candidates(
    request: MergeCandidatesRequest,
):

    if len(request.candidate_ids) < 2:

        raise HTTPException(
            status_code=400,
            detail=(
                "At least two candidates are "
                "required for merging."
            ),
        )

    object_ids = []

    for candidate_id in request.candidate_ids:

        object_ids.append(
            parse_object_id(candidate_id)
        )

    candidates = list(
        database.knowledge_candidates.find(
            {
                "_id": {
                    "$in": object_ids,
                },
                "status": "pending",
            }
        )
    )

    if len(candidates) != len(object_ids):

        raise HTTPException(
            status_code=404,
            detail=(
                "One or more pending knowledge "
                "candidates were not found."
            ),
        )

    # -----------------------------------------------------
    # First candidate becomes the primary candidate
    # -----------------------------------------------------

    primary = candidates[0]

    duplicates = candidates[1:]

    now = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Collect variants
    # -----------------------------------------------------

    question_variants = []

    for candidate in candidates:

        existing_variants = candidate.get(
            "question_variants",
            [],
        )

        if existing_variants:

            question_variants.extend(
                existing_variants
            )

        else:

            question_variants.append(
                candidate["question"]
            )

    # Remove duplicate questions while
    # preserving order.

    question_variants = list(
        dict.fromkeys(
            question_variants
        )
    )

    # -----------------------------------------------------
    # Merge keywords
    # -----------------------------------------------------

    keywords = []

    for candidate in candidates:

        keywords.extend(
            candidate.get(
                "keywords",
                [],
            )
        )

    keywords = list(
        dict.fromkeys(
            keyword
            for keyword in keywords
            if keyword
        )
    )

    # -----------------------------------------------------
    # Merge message IDs
    # -----------------------------------------------------

    message_ids = []

    for candidate in candidates:

        if candidate.get("message_id"):

            message_ids.append(
                candidate["message_id"]
            )

    message_ids = list(
        dict.fromkeys(
            message_ids
        )
    )

    # -----------------------------------------------------
    # Merge user IDs
    # -----------------------------------------------------

    user_ids = []

    for candidate in candidates:

        if candidate.get("user_id"):

            user_ids.append(
                candidate["user_id"]
            )

    user_ids = list(
        dict.fromkeys(
            user_ids
        )
    )

    # -----------------------------------------------------
    # Merge candidate IDs
    # -----------------------------------------------------

    merged_candidate_ids = [
        str(candidate["_id"])
        for candidate in candidates
    ]

    # -----------------------------------------------------
    # Calculate occurrences
    # -----------------------------------------------------

    occurrences = sum(
        candidate.get(
            "occurrences",
            1,
        )
        for candidate in candidates
    )

    # -----------------------------------------------------
    # Update primary candidate
    # -----------------------------------------------------

    database.knowledge_candidates.update_one(
        {
            "_id": primary["_id"],
        },
        {
            "$set": {

                "occurrences": occurrences,

                "question_variants":
                    question_variants,

                "keywords": keywords,

                "message_ids": message_ids,

                "user_ids": user_ids,

                "merged_candidate_ids":
                    merged_candidate_ids,

                "updated_at": now,
            }
        },
    )

    # -----------------------------------------------------
    # Remove duplicate candidates
    # -----------------------------------------------------

    duplicate_ids = [
        candidate["_id"]
        for candidate in duplicates
    ]

    database.knowledge_candidates.delete_many(
        {
            "_id": {
                "$in": duplicate_ids,
            }
        }
    )

    return {
        "status": "merged",

        "primary_candidate_id": str(
            primary["_id"]
        ),

        "merged_count": len(
            duplicates
        ),

        "occurrences": occurrences,

        "question_variants":
            question_variants,

        "keywords": keywords,
    }


# =========================================================
# Existing Knowledge
# =========================================================


@router.get(
    "/",
    summary="Get knowledge with pagination and search",
)
async def get_knowledge(
    page: int = Query(
        1,
        ge=1,
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100,
    ),

    search: str | None = Query(
        None,
        description="Search knowledge by keywords",
    ),
):

    skip = (
        page - 1
    ) * limit

    query = {}

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    if search and search.strip():

        search_term = search.strip()

        query = {
            "$or": [
                {
                    "title": {
                        "$regex": search_term,
                        "$options": "i",
                    }
                },
                {
                    "content": {
                        "$regex": search_term,
                        "$options": "i",
                    }
                },
                {
                    "topic": {
                        "$regex": search_term,
                        "$options": "i",
                    }
                },
                {
                    "category": {
                        "$regex": search_term,
                        "$options": "i",
                    }
                },
                {
                    "tags": {
                        "$elemMatch": {
                            "$regex": search_term,
                            "$options": "i",
                        }
                    }
                },
            ]
        }

    total = database.knowledge.count_documents(
        query
    )

    results = database.knowledge.find(
        query,
        {
            "_id": 1,
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
            "occurrences": 1,
            "question_variants": 1,
        },
    ).sort(
        "updated_at",
        -1,
    ).skip(
        skip
    ).limit(
        limit
    )

    knowledge = []

    for item in results:

        item = serialize_document(item)

        knowledge.append(item)

    total_pages = (
        (total + limit - 1)
        // limit
        if total
        else 0
    )

    return {
        "page": page,

        "limit": limit,

        "total": total,

        "total_pages": total_pages,

        "knowledge": knowledge,
    }


# =========================================================
# Get Existing Knowledge By ID
# =========================================================


@router.get(
    "/{knowledge_id}",
    summary="Get a knowledge entry",
)
async def get_knowledge_by_id(
    knowledge_id: str,
):

    object_id = parse_object_id(
        knowledge_id
    )

    knowledge = database.knowledge.find_one(
        {
            "_id": object_id,
        }
    )

    if not knowledge:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found.",
        )

    return serialize_document(
        knowledge
    )


# =========================================================
# Update Existing Knowledge
# =========================================================

class MergeKnowledgeRequest(BaseModel):
    knowledge_ids: list[str] = Field(
        min_length=2,
        description="IDs of knowledge entries to merge",
    )

    primary_id: str


@router.post(
    "/merge",
    summary="Merge existing knowledge entries",
)
async def merge_knowledge(
    request: MergeKnowledgeRequest,
):

    if len(request.knowledge_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two knowledge entries are required.",
        )

    if request.primary_id not in request.knowledge_ids:
        raise HTTPException(
            status_code=400,
            detail="Primary knowledge ID must be one of the selected entries.",
        )

    object_ids = []

    for knowledge_id in request.knowledge_ids:
        object_ids.append(
            parse_object_id(knowledge_id)
        )

    documents = list(
        database.knowledge.find(
            {
                "_id": {
                    "$in": object_ids,
                }
            }
        )
    )

    if len(documents) != len(object_ids):
        raise HTTPException(
            status_code=404,
            detail="One or more knowledge entries were not found.",
        )

    primary_object_id = parse_object_id(
        request.primary_id
    )

    primary = next(
        (
            item
            for item in documents
            if item["_id"] == primary_object_id
        ),
        None,
    )

    if not primary:
        raise HTTPException(
            status_code=404,
            detail="Primary knowledge entry not found.",
        )

    # -----------------------------------------------------
    # Merge tags
    # -----------------------------------------------------

    tags = []

    for document in documents:
        tags.extend(
            document.get("tags", [])
        )

    tags = list(
        dict.fromkeys(
            tag
            for tag in tags
            if tag
        )
    )

    # -----------------------------------------------------
    # Merge question variants
    # -----------------------------------------------------

    question_variants = []

    for document in documents:

        variants = document.get(
            "question_variants",
            [],
        )

        if variants:
            question_variants.extend(
                variants
            )

        elif document.get("title"):
            question_variants.append(
                document["title"]
            )

    question_variants = list(
        dict.fromkeys(
            question_variants
        )
    )

    # -----------------------------------------------------
    # Merge occurrences
    # -----------------------------------------------------

    occurrences = sum(
        document.get(
            "occurrences",
            1,
        )
        for document in documents
    )

    now = datetime.now(
        timezone.utc
    )

    # -----------------------------------------------------
    # Update primary
    # -----------------------------------------------------

    database.knowledge.update_one(
        {
            "_id": primary_object_id,
        },
        {
            "$set": {
                "tags": tags,
                "question_variants": question_variants,
                "occurrences": occurrences,
                "updated_at": now,
            }
        },
    )

    # -----------------------------------------------------
    # Delete duplicates
    # -----------------------------------------------------

    duplicate_ids = [
        document["_id"]
        for document in documents
        if document["_id"] != primary_object_id
    ]

    database.knowledge.delete_many(
        {
            "_id": {
                "$in": duplicate_ids,
            }
        }
    )

    updated = database.knowledge.find_one(
        {
            "_id": primary_object_id,
        }
    )

    return {
        "status": "merged",
        "primary_id": request.primary_id,
        "merged_count": len(duplicate_ids),
        "knowledge": serialize_document(
            updated
        ),
    }

@router.put(
    "/{knowledge_id}",
    summary="Update existing knowledge",
)
async def update_knowledge(
    knowledge_id: str,
    request: UpdateKnowledgeRequest,
):

    object_id = parse_object_id(
        knowledge_id
    )

    existing = database.knowledge.find_one(
        {
            "_id": object_id,
        }
    )

    if not existing:

        raise HTTPException(
            status_code=404,
            detail="Knowledge not found.",
        )

    updates = {}

    # -----------------------------------------------------
    # Only update fields that were supplied
    # -----------------------------------------------------

    if request.title is not None:

        title = request.title.strip()

        if title:

            updates["title"] = title

    if request.content is not None:

        content = request.content.strip()

        if content:

            updates["content"] = content

    if request.topic is not None:

        updates["topic"] = (
            request.topic.strip()
            or "general"
        )

    if request.category is not None:

        updates["category"] = (
            request.category.strip()
            or "general"
        )

    if request.tags is not None:

        updates["tags"] = list(
            dict.fromkeys(
                tag.strip()
                for tag in request.tags
                if tag.strip()
            )
        )

    if not updates:

        raise HTTPException(
            status_code=400,
            detail="No fields to update.",
        )

    updates["updated_at"] = datetime.now(
        timezone.utc
    )

    database.knowledge.update_one(
        {
            "_id": object_id,
        },
        {
            "$set": updates,
        },
    )

    updated = database.knowledge.find_one(
        {
            "_id": object_id,
        }
    )

    return {
        "status": "updated",
        "knowledge": serialize_document(
            updated
        ),
    }