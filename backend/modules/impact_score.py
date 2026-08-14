from datetime import datetime, timezone

from database import contributors


# =========================================================
# Impact Score Values
# =========================================================

SCORE = {
    "message": 1,
    "technical_question": 2,
    "helpful_answer": 5,
    "feedback": 3,
    "approved_knowledge": 10,
    "event_participation": 5,
    "event_contribution": 10,
    "bug_report_resolved": 5,
    "penalty": -2,
    "admin_penalty": -5,
}


# =========================================================
# Add Impact
# =========================================================

def add_impact(
    discord_id: str,
    points: int,
):
    """
    Add or subtract impact points for a contributor.
    """

    if not discord_id:
        return False

    result = contributors.update_one(
        {
            "discord_id": str(discord_id),
        },
        {
            "$inc": {
                "impact_score": points,
            },
            "$set": {
                "last_active": datetime.now(
                    timezone.utc
                ),
            },
        },
    )

    return result.modified_count > 0


# =========================================================
# Record Contribution
# =========================================================

def record_contribution(
    discord_id: str,
    contribution_type: str,
):
    """
    Record a meaningful contributor action
    and update their impact score.
    """

    points = SCORE.get(
        contribution_type,
        0,
    )

    if points == 0:
        return False

    return add_impact(
        discord_id=discord_id,
        points=points,
    )


# =========================================================
# Record Metric
# =========================================================

def increment_metric(
    discord_id: str,
    metric: str,
    amount: int = 1,
):
    """
    Increment a contributor metric.
    """

    if not discord_id:
        return False

    result = contributors.update_one(
        {
            "discord_id": str(discord_id),
        },
        {
            "$inc": {
                metric: amount,
            },
            "$set": {
                "last_active": datetime.now(
                    timezone.utc
                ),
            },
        },
    )

    return result.modified_count > 0


# =========================================================
# Get Contributor
# =========================================================

def get_contributor(
    discord_id: str,
):
    """
    Return contributor information.
    """

    return contributors.find_one(
        {
            "discord_id": str(
                discord_id
            )
        },
        {
            "_id": 0,
        },
    )


# =========================================================
# Leaderboard
# =========================================================

def get_leaderboard(
    limit: int = 10,
):
    """
    Return top contributors by impact score.
    """

    return list(
        contributors.find(
            {},
            {
                "_id": 0,

                "discord_id": 1,
                "username": 1,

                "impact_score": 1,

                "message_count": 1,
                "questions_asked": 1,
                "questions_answered": 1,
                "helpful_answers": 1,
                "knowledge_contributions": 1,

                "channels": 1,

                "first_seen": 1,
                "last_active": 1,
            },
        )
        .sort(
            [
                ("impact_score", -1),
                ("helpful_answers", -1),
                ("knowledge_contributions", -1),
                ("message_count", -1),
            ]
        )
        .limit(limit)
    )