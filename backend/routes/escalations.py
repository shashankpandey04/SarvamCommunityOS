from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
)

import database


router = APIRouter(
    prefix="/api/escalations",
    tags=["Escalations"],
)


# =========================================================
# Schemas
# =========================================================

class StatusUpdate(BaseModel):
    status: str


class EscalationMessage(BaseModel):
    user_id: str
    username: str
    content: str


# =========================================================
# Helpers
# =========================================================

ALLOWED_STATUSES = {
    "open",
    "in_progress",
    "resolved",
    "closed",
}


def serialize_escalation(
    escalation: dict,
) -> dict:

    escalation["_id"] = str(
        escalation["_id"]
    )

    return escalation


def get_escalation(
    escalation_id: str,
):

    if not ObjectId.is_valid(
        escalation_id
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid escalation ID.",
        )

    escalation = database.escalations.find_one(
        {
            "_id": ObjectId(
                escalation_id
            )
        }
    )

    if not escalation:

        raise HTTPException(
            status_code=404,
            detail="Escalation not found.",
        )

    return escalation


# =========================================================
# GET /api/escalations
# =========================================================

@router.get(
    "/",
    summary="Get support escalations",
)
async def get_escalations(
    status: str | None = Query(
        default=None,
    ),
    guild_id: str | None = Query(
        default=None,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
):

    query = {}

    if status:

        if status not in ALLOWED_STATUSES:

            raise HTTPException(
                status_code=400,
                detail="Invalid escalation status.",
            )

        query["status"] = status

    if guild_id:
        query["guild_id"] = guild_id

    results = (
        database.escalations
        .find(
            query,
            {
                "_id": 1,
                "question": 1,
                "user_id": 1,
                "username": 1,
                "guild_id": 1,
                "channel_id": 1,
                "thread_id": 1,
                "topic": 1,
                "bot_answer": 1,
                "status": 1,
                "messages": 1,
                "created_at": 1,
                "updated_at": 1,
                "closed_at": 1,
                "closed_by": 1,
            },
        )
        .sort(
            "created_at",
            -1,
        )
        .skip(skip)
        .limit(limit)
    )

    return [
        serialize_escalation(
            result
        )
        for result in results
    ]


# =========================================================
# GET /api/escalations/{escalation_id}
# =========================================================

@router.get(
    "/{escalation_id}",
    summary="Get a single escalation",
)
async def get_escalation_by_id(
    escalation_id: str,
):

    escalation = get_escalation(
        escalation_id
    )

    return serialize_escalation(
        escalation
    )


# =========================================================
# PATCH /api/escalations/{escalation_id}/status
# =========================================================

@router.patch(
    "/{escalation_id}/status",
    summary="Update escalation status",
)
async def update_escalation_status(
    escalation_id: str,
    payload: StatusUpdate,
):

    status = payload.status.strip().lower()

    if status not in ALLOWED_STATUSES:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. "
                f"Allowed values: "
                f"{', '.join(sorted(ALLOWED_STATUSES))}"
            ),
        )

    escalation = get_escalation(
        escalation_id
    )

    now = datetime.now(
        timezone.utc
    )

    update = {
        "status": status,
        "updated_at": now,
    }

    if status in {
        "resolved",
        "closed",
    }:

        update["closed_at"] = now

    else:

        update["closed_at"] = None
        update["closed_by"] = None

    database.escalations.update_one(
        {
            "_id": escalation["_id"]
        },
        {
            "$set": update
        },
    )

    updated = get_escalation(
        escalation_id
    )

    return serialize_escalation(
        updated
    )


# =========================================================
# POST /api/escalations/{escalation_id}/messages
# =========================================================

@router.post(
    "/{escalation_id}/messages",
    summary="Send a message to an escalation",
)
async def send_escalation_message(
    escalation_id: str,
    payload: EscalationMessage,
    request: Request,
):

    escalation = get_escalation(
        escalation_id
    )

    content = payload.content.strip()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # -------------------------------------------------
    # Discord Bot
    # -------------------------------------------------

    bot = request.app.state.discord_bot

    if bot is None:
        raise HTTPException(
            status_code=503,
            detail="Discord bot is not ready.",
        )

    # -------------------------------------------------
    # Discord Thread
    # -------------------------------------------------

    thread_id = escalation.get(
        "thread_id"
    )

    if not thread_id:
        raise HTTPException(
            status_code=400,
            detail="Escalation has no Discord thread.",
        )

    try:

        thread = bot.get_channel(
            int(thread_id)
        )

        if thread is None:

            thread = await bot.fetch_channel(
                int(thread_id)
            )

    except Exception as exc:

        raise HTTPException(
            status_code=404,
            detail=(
                "Discord thread not found: "
                f"{exc}"
            ),
        )

    # -------------------------------------------------
    # Send to Discord
    # -------------------------------------------------

    try:

        discord_message = await thread.send(
            content
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to send Discord message: "
                f"{exc}"
            ),
        )

    # -------------------------------------------------
    # Save Message
    # -------------------------------------------------

    now = datetime.now(
        timezone.utc
    )

    message = {
        "message_id": str(
            discord_message.id
        ),
        "user_id": payload.user_id,
        "username": payload.username,
        "content": content,
        "source": "dashboard",
        "created_at": now,
    }

    database.escalations.update_one(
        {
            "_id": escalation["_id"]
        },
        {
            "$push": {
                "messages": message
            },
            "$set": {
                "status": "in_progress",
                "updated_at": now,
            },
        },
    )

    return {
        "success": True,
        "message": message,
    }

# =========================================================
# DELETE /api/escalations/{escalation_id}
# =========================================================

@router.delete(
    "/{escalation_id}",
    summary="Delete an escalation",
)
async def delete_escalation(
    escalation_id: str,
):

    escalation = get_escalation(
        escalation_id
    )

    database.escalations.delete_one(
        {
            "_id": escalation["_id"]
        }
    )

    return {
        "success": True,
        "message": "Escalation deleted.",
        "id": escalation_id,
    }