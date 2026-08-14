from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/support",
    tags=["Support"],
)


# =========================================================
# Escalations
# =========================================================

@router.get(
    "/escalations",
    summary="Get support escalations",
)
async def get_escalations():

    results = database.escalations.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "created_at",
        -1,
    )

    return list(results)