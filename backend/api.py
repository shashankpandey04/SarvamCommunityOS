from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import FastAPI, HTTPException

import database

app = FastAPI(
    title="Sarvam CommunityOS API",
    version="0.1.0",
)

def get_date_range(
    days: int | None = 30,
):
    """
    Return the UTC start and end timestamps
    for an analytics query.

    days=None means all available data.
    """

    end = datetime.now(timezone.utc)

    if days is None:
        return None, end

    start = end - timedelta(
        days=days
    )

    return start, end


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "communityos",
    }


# --------------------------------------------------
# Community Overview
# --------------------------------------------------

@app.get("/api/community/overview")
async def community_overview():

    total_users = database.users.count_documents({})

    total_messages = database.messages.count_documents({})

    total_questions = database.messages.count_documents({
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        }
    })

    resolved = database.messages.count_documents({
        "resolved": True
    })

    escalated = database.messages.count_documents({
        "escalated": True
    })

    resolution_rate = (
        round((resolved / total_questions) * 100, 2)
        if total_questions
        else 0
    )

    return {
        "members": total_users,
        "messages": total_messages,
        "questions": total_questions,
        "resolved": resolved,
        "escalated": escalated,
        "resolution_rate": resolution_rate,
    }


# --------------------------------------------------
# Trending Topics
# --------------------------------------------------

@app.get("/api/community/trends")
async def community_trends():

    pipeline = [
        {
            "$group": {
                "_id": "$topic",
                "mentions": {
                    "$sum": 1
                },
            }
        },
        {
            "$sort": {
                "mentions": -1
            }
        },
        {
            "$limit": 10
        },
    ]

    results = database.messages.aggregate(
        pipeline
    )

    return [
        {
            "topic": item["_id"],
            "mentions": item["mentions"],
        }
        for item in results
    ]


# --------------------------------------------------
# Community Signals
# --------------------------------------------------

@app.get("/api/community/signals")
async def community_signals():

    results = database.insights.find(
        {},
        {"_id": 0}
    ).sort(
        "change_percent",
        -1,
    )

    return list(results)


# --------------------------------------------------
# Support / Escalations
# --------------------------------------------------

@app.get("/api/support/escalations")
async def support_escalations():

    results = database.escalations.find(
        {},
        {"_id": 0}
    ).sort(
        "created_at",
        -1,
    )

    return list(results)


# --------------------------------------------------
# Feedback
# --------------------------------------------------

@app.get("/api/feedback")
async def get_feedback():

    results = database.feedback.find(
        {},
        {"_id": 0}
    ).sort(
        "created_at",
        -1,
    )

    return list(results)


# --------------------------------------------------
# Contributors
# --------------------------------------------------

@app.get("/api/contributors")
async def get_contributors():

    results = database.contributors.find(
        {},
        {"_id": 0}
    ).sort(
        "impact_score",
        -1,
    )

    return list(results)


# --------------------------------------------------
# Events
# --------------------------------------------------

@app.get("/api/events")
async def get_events():

    results = database.events.find(
        {},
        {"_id": 0}
    ).sort(
        "date",
        1,
    )

    return list(results)


# --------------------------------------------------
# Documents
# --------------------------------------------------

@app.get("/api/documents")
async def get_documents():

    results = database.documents.find(
        {},
        {"_id": 0}
    )

    return list(results)

# --------------------------------------------------
# Knowledge Candidates
# --------------------------------------------------

@app.get("/api/knowledge/candidates")
async def get_knowledge_candidates():

    results = database.knowledge_candidates.find(
        {
            "status": "pending"
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
        }
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

@app.post(
    "/api/knowledge/candidates/{candidate_id}/approve"
)
async def approve_knowledge_candidate(
    candidate_id: str,
):

    try:
        object_id = ObjectId(candidate_id)

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
            detail="Pending knowledge candidate not found.",
        )

    now = datetime.now(timezone.utc)

    # ---------------------------------------------
    # Create trusted knowledge
    # ---------------------------------------------

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

    # ---------------------------------------------
    # Mark candidate approved
    # ---------------------------------------------

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

@app.post(
    "/api/knowledge/candidates/{candidate_id}/reject"
)
async def reject_knowledge_candidate(
    candidate_id: str,
):

    try:
        object_id = ObjectId(candidate_id)

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
            detail="Pending knowledge candidate not found.",
        )

    now = datetime.now(timezone.utc)

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

# --------------------------------------------------
# Analytics Overview
# --------------------------------------------------

@app.get("/api/analytics/overview")
async def analytics_overview():

    total_questions = database.messages.count_documents({})

    resolved = database.messages.count_documents({
        "resolved": True
    })

    escalated = database.messages.count_documents({
        "escalated": True
    })

    knowledge_found = database.messages.count_documents({
        "knowledge_found": True
    })

    sarvam_fallback = database.messages.count_documents({
        "sarvam_fallback": True
    })

    # ----------------------------------------------
    # Calculated Metrics
    # ----------------------------------------------

    resolution_rate = (
        round(
            (resolved / total_questions) * 100,
            2,
        )
        if total_questions
        else 0
    )

    knowledge_coverage_rate = (
        round(
            (knowledge_found / total_questions) * 100,
            2,
        )
        if total_questions
        else 0
    )

    fallback_rate = (
        round(
            (sarvam_fallback / total_questions) * 100,
            2,
        )
        if total_questions
        else 0
    )

    return {
        "total_questions": total_questions,

        "resolved": resolved,

        "escalated": escalated,

        "knowledge_found": knowledge_found,

        "sarvam_fallback": sarvam_fallback,

        "resolution_rate": resolution_rate,

        "knowledge_coverage_rate": knowledge_coverage_rate,

        "fallback_rate": fallback_rate,
    }
# --------------------------------------------------
# Analytics Activity
# --------------------------------------------------

@app.get("/api/analytics/activity")
async def analytics_activity(
    days: int | None = 30,
):

    start, end = get_date_range(days)

    match = {}

    if start:
        match["created_at"] = {
            "$gte": start,
            "$lte": end,
        }

    pipeline = [
        {
            "$match": match
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at",
                    }
                },

                "messages": {
                    "$sum": 1
                },

                "questions": {
                    "$sum": {
                        "$cond": [
                            {
                                "$in": [
                                    "$intent",
                                    [
                                        "technical_question",
                                        "onboarding",
                                        "program_question",
                                    ],
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },

                "resolved": {
                    "$sum": {
                        "$cond": [
                            "$resolved",
                            1,
                            0,
                        ]
                    }
                },

                "escalated": {
                    "$sum": {
                        "$cond": [
                            "$escalated",
                            1,
                            0,
                        ]
                    }
                },

                "fallback": {
                    "$sum": {
                        "$cond": [
                            "$sarvam_fallback",
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
    ]

    results = database.messages.aggregate(
        pipeline
    )

    return [
        {
            "date": item["_id"],
            "messages": item["messages"],
            "questions": item["questions"],
            "resolved": item["resolved"],
            "escalated": item["escalated"],
            "fallback": item["fallback"],
        }
        for item in results
    ]

# --------------------------------------------------
# Analytics Topics
# --------------------------------------------------

# --------------------------------------------------
# Analytics — Topics
# --------------------------------------------------

@app.get("/api/analytics/topics")
async def analytics_topics():

    pipeline = [
        {
            "$match": {
                "intent": {
                    "$in": [
                        "technical_question",
                        "onboarding",
                        "program_question",
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$topic",
                "questions": {
                    "$sum": 1
                },
                "resolved": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$resolved",
                                    True,
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "escalated": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$escalated",
                                    True,
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "knowledge_found": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$knowledge_found",
                                    True,
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
                "sarvam_fallback": {
                    "$sum": {
                        "$cond": [
                            {
                                "$eq": [
                                    "$sarvam_fallback",
                                    True,
                                ]
                            },
                            1,
                            0,
                        ]
                    }
                },
            }
        },
        {
            "$sort": {
                "questions": -1
            }
        },
        {
            "$limit": 10
        },
    ]

    results = database.messages.aggregate(
        pipeline
    )

    topics = []

    for item in results:

        questions = item["questions"]

        resolution_rate = (
            round(
                (
                    item["resolved"]
                    / questions
                ) * 100,
                2,
            )
            if questions
            else 0
        )

        topics.append({
            "topic": item["_id"] or "general",

            "questions": questions,

            "resolved": item["resolved"],

            "escalated": item["escalated"],

            "knowledge_found": item[
                "knowledge_found"
            ],

            "sarvam_fallback": item[
                "sarvam_fallback"
            ],

            "resolution_rate": resolution_rate,
        })

    return topics

# --------------------------------------------------
# Analytics Knowledge
# --------------------------------------------------

@app.get("/api/analytics/knowledge")
async def analytics_knowledge(
    days: int | None = 30,
):

    start, end = get_date_range(days)

    candidate_filter = {}

    if start:
        candidate_filter["created_at"] = {
            "$gte": start,
            "$lte": end,
        }

    total_candidates = (
        database.knowledge_candidates.count_documents(
            candidate_filter
        )
    )

    pending_candidates = (
        database.knowledge_candidates.count_documents({
            **candidate_filter,
            "status": "pending",
        })
    )

    approved_candidates = (
        database.knowledge_candidates.count_documents({
            **candidate_filter,
            "status": "approved",
        })
    )

    rejected_candidates = (
        database.knowledge_candidates.count_documents({
            **candidate_filter,
            "status": "rejected",
        })
    )

    total_knowledge = (
        database.knowledge.count_documents({})
    )

    official_knowledge = (
        database.knowledge.count_documents({
            "source": "official",
        })
    )

    generated_knowledge = (
        database.knowledge.count_documents({
            "source": "communityos_candidate",
        })
    )

    return {
        "period": {
            "days": days,
            "start": start,
            "end": end,
        },

        "knowledge": {
            "total": total_knowledge,
            "official": official_knowledge,
            "generated": generated_knowledge,
        },

        "candidates": {
            "total": total_candidates,
            "pending": pending_candidates,
            "approved": approved_candidates,
            "rejected": rejected_candidates,
        },
    }