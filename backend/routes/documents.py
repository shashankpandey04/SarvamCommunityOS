import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from document_service import DocumentService
from sarvam_client import SarvamService
from config import SARVAM_API_KEY


import database


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


# =========================================================
# Services
# =========================================================

sarvam_service = SarvamService(
    SARVAM_API_KEY
)

document_service = DocumentService(
    sarvam=sarvam_service
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
            "_id": 1,
            "filename": 1,
            "status": 1,
            "source": 1,
            "knowledge_count": 1,
            "error": 1,
            "created_at": 1,
            "updated_at": 1,
        },
    ).sort(
        "created_at",
        -1,
    )

    documents = []

    for item in results:

        item["_id"] = str(
            item["_id"]
        )

        documents.append(item)

    return documents


# =========================================================
# Upload PDF
# =========================================================

@router.post(
    "/upload",
    summary="Upload a PDF and create knowledge",
)
async def upload_document(
    file: UploadFile = File(...),
):

    # -----------------------------------------------------
    # Validate file
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # -----------------------------------------------------
    # Save temporary file
    # -----------------------------------------------------

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temp_file:

            temp_path = temp_file.name

            content = await file.read()

            temp_file.write(
                content
            )

        # -------------------------------------------------
        # Process document
        # -------------------------------------------------

        result = await document_service.process_pdf(
            file_path=temp_path
        )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        # -------------------------------------------------
        # Cleanup temporary PDF
        # -------------------------------------------------

        if temp_path and os.path.exists(
            temp_path
        ):

            os.remove(
                temp_path
            )