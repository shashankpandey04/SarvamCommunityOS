from datetime import datetime, timedelta, timezone

import database


# =========================================================
# Configuration
# =========================================================

DEFAULT_DAYS = 7

FALLBACK_RATE_THRESHOLD = 40
ESCALATION_RATE_THRESHOLD = 30
TOPIC_GROWTH_THRESHOLD = 50

PENDING_CANDIDATE_THRESHOLD = 5
REPEATED_QUESTION_THRESHOLD = 3


# =========================================================
# Helpers
# =========================================================

def _date_range(days: int = DEFAULT_DAYS):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    return start, end


def _base_query(start, end):
    return {
        "created_at": {
            "$gte": start,
            "$lte": end,
        }
    }


def _create_insight(
    *,
    insight_type: str,
    severity: str,
    title: str,
    message: str,
    suggestion: str,
    action_type: str | None = None,
    action_target: str | None = None,
    topic: str | None = None,
    metric: dict | None = None,
):
    now = datetime.now(timezone.utc)

    insight = {
        "type": insight_type,
        "severity": severity,

        "title": title,
        "message": message,
        "suggestion": suggestion,

        "topic": topic,

        "metric": metric or {},

        "action": {
            "type": action_type,
            "target": action_target,
        },

        "created_at": now,
        "updated_at": now,
    }

    return insight


# =========================================================
# Knowledge Gap Detection
# =========================================================

def _detect_knowledge_gaps(
    start,
    end,
):
    query = _base_query(start, end)

    questions = database.messages.count_documents({
        **query,
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
    })

    if questions == 0:
        return []

    fallback_count = database.messages.count_documents({
        **query,
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
        "sarvam_fallback": True,
    })

    fallback_rate = (
        fallback_count / questions
    ) * 100

    if fallback_rate < FALLBACK_RATE_THRESHOLD:
        return []

    return [
        _create_insight(
            insight_type="knowledge_gap",
            severity="high",

            title="Knowledge coverage is low",

            message=(
                f"{fallback_count} of {questions} "
                "questions required Sarvam fallback."
            ),

            suggestion=(
                "Review the missing topics and "
                "update or upload relevant documentation."
            ),

            action_type="review_knowledge",
            action_target="/knowledge",

            metric={
                "questions": questions,
                "fallbacks": fallback_count,
                "fallback_rate": round(
                    fallback_rate,
                    2,
                ),
            },
        )
    ]


# =========================================================
# Pending Knowledge Candidates
# =========================================================

def _detect_pending_candidates():
    pending = database.knowledge_candidates.count_documents({
        "status": "pending",
    })

    if pending < PENDING_CANDIDATE_THRESHOLD:
        return []

    return [
        _create_insight(
            insight_type="knowledge_review",
            severity="medium",

            title="Knowledge candidates need review",

            message=(
                f"{pending} AI-generated knowledge "
                "candidates are waiting for review."
            ),

            suggestion=(
                "Review pending candidates and approve "
                "useful answers for the knowledge base."
            ),

            action_type="review_candidates",
            action_target="/knowledge/candidates",

            metric={
                "pending_candidates": pending,
            },
        )
    ]


# =========================================================
# Escalation Detection
# =========================================================

def _detect_escalations(
    start,
    end,
):
    query = _base_query(start, end)

    questions = database.messages.count_documents({
        **query,
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
    })

    if questions == 0:
        return []

    escalated = database.messages.count_documents({
        **query,
        "intent": {
            "$in": [
                "technical_question",
                "onboarding",
                "program_question",
            ]
        },
        "escalated": True,
    })

    escalation_rate = (
        escalated / questions
    ) * 100

    if escalation_rate < ESCALATION_RATE_THRESHOLD:
        return []

    return [
        _create_insight(
            insight_type="high_escalation",
            severity="high",

            title="High support escalation rate",

            message=(
                f"{escalated} of {questions} questions "
                "required human escalation."
            ),

            suggestion=(
                "Review escalated questions and improve "
                "knowledge coverage for recurring issues."
            ),

            action_type="review_escalations",
            action_target="/support/escalations",

            metric={
                "questions": questions,
                "escalated": escalated,
                "escalation_rate": round(
                    escalation_rate,
                    2,
                ),
            },
        )
    ]


# =========================================================
# Trending Topics
# =========================================================

def _detect_trending_topics(
    start,
    end,
):
    current_pipeline = [
        {
            "$match": {
                **_base_query(start, end),
                "topic": {
                    "$exists": True,
                    "$ne": None,
                },
            }
        },
        {
            "$group": {
                "_id": "$topic",
                "count": {
                    "$sum": 1,
                },
            }
        },
    ]

    current = {
        item["_id"]: item["count"]
        for item in database.messages.aggregate(
            current_pipeline
        )
    }

    previous_start = start - (
        end - start
    )

    previous_pipeline = [
        {
            "$match": {
                **_base_query(
                    previous_start,
                    start,
                ),
                "topic": {
                    "$exists": True,
                    "$ne": None,
                },
            }
        },
        {
            "$group": {
                "_id": "$topic",
                "count": {
                    "$sum": 1,
                },
            }
        },
    ]

    previous = {
        item["_id"]: item["count"]
        for item in database.messages.aggregate(
            previous_pipeline
        )
    }

    insights = []

    for topic, current_count in current.items():

        previous_count = previous.get(
            topic,
            0,
        )

        # New topic
        if previous_count == 0:

            if current_count < 3:
                continue

            growth = 100

        else:

            growth = (
                (
                    current_count
                    - previous_count
                )
                / previous_count
            ) * 100

        if growth < TOPIC_GROWTH_THRESHOLD:
            continue

        insights.append(
            _create_insight(
                insight_type="trending_topic",
                severity="medium",

                title=f"{topic} is trending",

                message=(
                    f"Questions about {topic} increased "
                    f"from {previous_count} to "
                    f"{current_count}."
                ),

                suggestion=(
                    "Consider creating or updating "
                    "documentation, a guide, or a workshop "
                    "for this topic."
                ),

                action_type="review_topic",
                action_target=f"/knowledge?topic={topic}",

                topic=topic,

                metric={
                    "current_questions": current_count,
                    "previous_questions": previous_count,
                    "growth_percent": round(
                        growth,
                        2,
                    ),
                },
            )
        )

    return insights


# =========================================================
# Repeated Questions
# =========================================================

def _detect_repeated_questions(
    start,
    end,
):
    pipeline = [
        {
            "$match": {
                **_base_query(start, end),
                "content": {
                    "$exists": True,
                    "$ne": "",
                },
                "intent": {
                    "$in": [
                        "technical_question",
                        "onboarding",
                        "program_question",
                    ]
                },
            }
        },
        {
            "$group": {
                "_id": "$content",
                "count": {
                    "$sum": 1,
                },
                "topic": {
                    "$first": "$topic",
                },
            }
        },
        {
            "$match": {
                "count": {
                    "$gte": REPEATED_QUESTION_THRESHOLD,
                }
            }
        },
        {
            "$sort": {
                "count": -1,
            }
        },
        {
            "$limit": 5,
        },
    ]

    results = database.messages.aggregate(
        pipeline
    )

    insights = []

    for item in results:

        question = item["_id"]
        count = item["count"]
        topic = item.get("topic")

        insights.append(
            _create_insight(
                insight_type="repeated_question",
                severity="medium",

                title="Repeated community question",

                message=(
                    f"The same question has appeared "
                    f"{count} times."
                ),

                suggestion=(
                    "Create a knowledge article or FAQ "
                    "to answer this question automatically."
                ),

                action_type="create_knowledge",
                action_target="/knowledge/create",

                topic=topic,

                metric={
                    "occurrences": count,
                    "question": question,
                },
            )
        )

    return insights


# =========================================================
# Generate Insights
# =========================================================

def generate_insights(
    days: int = DEFAULT_DAYS,
):
    """
    Analyze recent CommunityOS data and generate
    actionable dashboard insights.

    Returns the generated insights without saving them.
    """

    start, end = _date_range(days)

    insights = []

    insights.extend(
        _detect_knowledge_gaps(
            start,
            end,
        )
    )

    insights.extend(
        _detect_pending_candidates()
    )

    insights.extend(
        _detect_escalations(
            start,
            end,
        )
    )

    insights.extend(
        _detect_trending_topics(
            start,
            end,
        )
    )

    insights.extend(
        _detect_repeated_questions(
            start,
            end,
        )
    )

    return insights


# =========================================================
# Save Insights
# =========================================================

def refresh_insights(
    days: int = DEFAULT_DAYS,
):
    """
    Generate fresh insights and replace the existing
    generated dashboard insights.
    """

    generated = generate_insights(
        days=days
    )

    if generated:
        result = database.insights.insert_many(
            generated
        )

        for insight, inserted_id in zip(
            generated,
            result.inserted_ids,
        ):
            insight["_id"] = str(
                inserted_id
            )

    return generated

# =========================================================
# Get Current Insights
# =========================================================

def get_insights(
    limit: int = 20,
):
    """
    Return currently stored dashboard insights.
    """

    return list(
        database.insights.find(
            {},
            {
                "_id": 0,
            },
        )
        .sort(
            [
                ("severity", -1),
                ("created_at", -1),
            ]
        )
        .limit(limit)
    )