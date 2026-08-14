from fastapi import APIRouter

import database


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


# =========================================================
# Get Documents
# =========================================================

@router.get(
    "",
    summary="Get uploaded documents",
)
async def get_documents():

    results = database.documents.find(
        {},
        {
            "_id": 0,
        },
    )

    return list(results)