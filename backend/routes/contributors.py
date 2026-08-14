from fastapi import APIRouter, HTTPException

import database


router = APIRouter(
    prefix="/api/contributors",
    tags=["Contributors"],
)


# =========================================================
# Leaderboard
# =========================================================

@router.get(
    "/leaderboard",
    summary="Get contributor leaderboard",
)
async def contributor_leaderboard(
    limit: int = 10,
):
    """
    Return top contributors ranked by impact score.
    """

    limit = max(
        1,
        min(limit, 100),
    )

    contributors = list(
        database.contributors.find(
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

    return contributors


# =========================================================
# Contributor Profile
# =========================================================

@router.get(
    "/{discord_id}",
    summary="Get contributor details",
)
async def get_contributor(
    discord_id: str,
):
    """
    Return contribution statistics for one Discord user.
    """

    contributor = database.contributors.find_one(
        {
            "discord_id": str(discord_id),
        },
        {
            "_id": 0,
        },
    )

    if not contributor:
        raise HTTPException(
            status_code=404,
            detail="Contributor not found.",
        )

    return contributor