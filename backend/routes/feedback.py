from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/feedback",
    tags=["Feedback"],
)


# =========================================================
# Get Feedback
# =========================================================

@router.get(
    "",
    summary="Get community feedback",
)
async def get_feedback():

    results = database.feedback.find(
        {},
        {
            "_id": 0,
        },
    ).sort(
        "created_at",
        -1,
    )

    return list(results)