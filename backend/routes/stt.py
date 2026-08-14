import os
import tempfile

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    File,
)

from sarvam_client import SarvamService
from config import SARVAM_API_KEY


router = APIRouter(
    prefix="/api",
    tags=["Sarvam AI"],
)


sarvam = SarvamService(
    SARVAM_API_KEY
)


@router.post(
    "/stt",
    summary="Convert speech to text",
)
async def speech_to_text(
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No audio file provided.",
        )

    # Supported audio formats according to
    # Sarvam's STT REST API.
    allowed_extensions = {
        ".wav",
        ".mp3",
        ".aac",
        ".flac",
        ".ogg",
    }

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported audio format. "
                "Supported formats: WAV, MP3, AAC, FLAC, OGG."
            ),
        )

    temp_path = None

    try:

        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty.",
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_file.write(audio_bytes)

            temp_path = temp_file.name

        # Existing SarvamService method
        result = await sarvam.transcribe(
            temp_path
        )

        return {
            "success": True,
            "transcript": getattr(
                result,
                "transcript",
                "",
            ),
            "language_code": getattr(
                result,
                "language_code",
                None,
            ),
            "request_id": getattr(
                result,
                "request_id",
                None,
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:

        if temp_path and os.path.exists(
            temp_path
        ):
            os.remove(temp_path)