from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)


# =========================================================
# Helpers
# =========================================================

QUESTION_INTENTS = [
    "technical_question",
    "onboarding",
    "program_question",
]


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

    start = end - timedelta(days=days)

    return start, end


# =========================================================
# Overview
# =========================================================

@router.get(
    "/overview",
    summary="Get CommunityOS analytics overview",
)
async def analytics_overview():

    question_filter = {
        "intent": {
            "$in": QUESTION_INTENTS,
        }
    }

    total_questions = database.messages.count_documents(
        question_filter
    )

    resolved = database.messages.count_documents({
        **question_filter,
        "resolved": True,
    })

    escalated = database.messages.count_documents({
        **question_filter,
        "escalated": True,
    })

    knowledge_found = database.messages.count_documents({
        **question_filter,
        "knowledge_found": True,
    })

    sarvam_fallback = database.messages.count_documents({
        **question_filter,
        "sarvam_fallback": True,
    })

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


# =========================================================
# Activity
# =========================================================

@router.get(
    "/activity",
    summary="Get CommunityOS activity over time",
)
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
            "$match": match,
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
                    "$sum": 1,
                },

                "questions": {
                    "$sum": {
                        "$cond": [
                            {
                                "$in": [
                                    "$intent",
                                    QUESTION_INTENTS,
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
                "_id": 1,
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


# =========================================================
# Topics
# =========================================================

@router.get(
    "/topics",
    summary="Get analytics grouped by topic",
)
async def analytics_topics():

    pipeline = [
        {
            "$match": {
                "intent": {
                    "$in": QUESTION_INTENTS,
                }
            }
        },
        {
            "$group": {
                "_id": "$topic",

                "questions": {
                    "$sum": 1,
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
                "questions": -1,
            }
        },
        {
            "$limit": 10,
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


# =========================================================
# Knowledge Analytics
# =========================================================

@router.get(
    "/knowledge",
    summary="Get knowledge base analytics",
)
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