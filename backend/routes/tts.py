import base64

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from config import SARVAM_API_KEY
from sarvam import SarvamService


router = APIRouter(
    prefix="/api",
    tags=["Sarvam AI"],
)


sarvam = SarvamService(
    SARVAM_API_KEY
)


class TTSRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=2500,
    )

    target_language_code: str = Field(
        default="hi-IN",
    )

    speaker: str = Field(
        default="shubh",
    )


@router.post(
    "/tts",
    summary="Convert text to speech",
)
async def text_to_speech(
    request: TTSRequest,
):

    try:

        result = await sarvam.text_to_speech(
            text=request.text,
            target_language_code=request.target_language_code,
            speaker=request.speaker,
        )

        audio_base64 = result.audios[0]

        audio_bytes = base64.b64decode(
            audio_base64
        )

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": (
                    'inline; filename="communityos-tts.wav"'
                )
            },
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )