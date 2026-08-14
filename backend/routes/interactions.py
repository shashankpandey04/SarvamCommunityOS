from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/interactions",
    tags=["Interactions"],
)


# =========================================================
# Get Interactions
# =========================================================

@router.get(
    "",
    summary="Get community interactions",
)
async def get_interactions():

    results = database.interactions.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "created_at",
        -1,
    )

    return list(results)