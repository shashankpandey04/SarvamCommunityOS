from fastapi import FastAPI

import database


app = FastAPI(
    title="Sarvam CommunityOS API",
    version="0.1.0",
)


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