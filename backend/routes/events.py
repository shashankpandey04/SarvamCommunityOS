from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


# =========================================================
# Get Events
# =========================================================

@router.get(
    "",
    summary="Get community events",
)
async def get_events():

    results = database.events.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "created_at",
        -1,
    )

    return list(results)