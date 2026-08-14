from fastapi import APIRouter
from modules.insights import refresh_insights, delete_existing_insights
import database


router = APIRouter(
    prefix="/api/community",
    tags=["Community"],
)


# =========================================================
# Community Overview
# =========================================================

@router.get(
    "/overview",
    summary="Get community overview",
)
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
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
        "resolved": True,
    })

    escalated = database.messages.count_documents({
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
        "escalated": True,
    })

    resolution_rate = (
        round(
            (resolved / total_questions) * 100,
            2,
        )
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


# =========================================================
# Trending Topics
# =========================================================

@router.get(
    "/trends",
    summary="Get trending community topics",
)
async def community_trends():

    pipeline = [
        {
            "$match": {
                "topic": {
                    "$exists": True,
                    "$ne": None,
                }
            }
        },
        {
            "$group": {
                "_id": "$topic",
                "mentions": {
                    "$sum": 1,
                },
            }
        },
        {
            "$sort": {
                "mentions": -1,
            }
        },
        {
            "$limit": 10,
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


# =========================================================
# Community Signals
# =========================================================

@router.get(
    "/signals",
    summary="Get community signals",
)
async def community_signals():

    results = database.insights.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "change_percent",
        -1,
    )

    return list(results)

# =========================================================
# Refresh Community Insights
# =========================================================
@router.post(
    "/signals/refresh",
    summary="Refresh community insights",
)
async def refresh_community_insights():

    delete_existing_insights()

    insights = refresh_insights()

    for insight in insights:
        insight.pop(
            "_id",
            None,
        )

    return {
        "status": "refreshed",
        "count": len(insights),
        "insights": insights,
    }