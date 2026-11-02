import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import RawMessage, PlacementDrive
from schemas import RawMessageCreate, RawMessageResponse

from nlp.processor import process_message
from nlp.storage import (
    get_or_create_placement_drive_for_message,
    store_extracted_information,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/messages",
    tags=["Raw Messages"]
)


# ============================================================
# CREATE RAW MESSAGE
# ============================================================

@router.post(
    "/",
    response_model=RawMessageResponse
)
def create_message(
    message: RawMessageCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate placement drive if explicitly provided
    # --------------------------------------------------------

    if message.placement_drive_id is not None:

        placement_drive = db.query(
            PlacementDrive
        ).filter(
            PlacementDrive.id == message.placement_drive_id
        ).first()

        if not placement_drive:
            raise HTTPException(
                status_code=404,
                detail="Placement drive not found"
            )

    # --------------------------------------------------------
    # Create raw message
    # --------------------------------------------------------

    new_message = RawMessage(
        message_id=message.message_id,
        source=message.source,
        sender=message.sender,
        message_text=message.message_text,
        message_date=message.message_date,
        placement_drive_id=message.placement_drive_id
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message


# ============================================================
# GET ALL RAW MESSAGES
# ============================================================

@router.get(
    "/",
    response_model=list[RawMessageResponse]
)
def get_messages(
    db: Session = Depends(get_db)
):

    messages = db.query(
        RawMessage
    ).all()

    return messages


# ============================================================
# PROCESS RAW MESSAGE
# ============================================================

@router.post(
    "/{message_id}/process"
)
def process_raw_message(
    message_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find raw message
    # --------------------------------------------------------

    message = db.query(
        RawMessage
    ).filter(
        RawMessage.id == message_id
    ).first()

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    try:
        result = process_message(message.message_text)
        extracted = result.get("extracted_information") or {}
        company_name = extracted.get("company")

        if company_name:
            placement_drive = get_or_create_placement_drive_for_message(
                db=db,
                company_name=company_name,
                message_text=message.message_text,
            )
        else:
            placement_drive = None
            if message.placement_drive_id is not None:
                placement_drive = db.query(PlacementDrive).filter(
                    PlacementDrive.id == message.placement_drive_id
                ).first()

            if placement_drive is None:
                error = "Company not detected; no placement drive could be linked."
                logger.warning(
                    "Unable to process RawMessage %s: %s",
                    message.id,
                    error,
                )
                raise HTTPException(
                    status_code=422,
                    detail={
                        "status": "failed",
                        "message_id": message.id,
                        "processed": False,
                        "error": error,
                    },
                )

        if placement_drive is None:
            raise RuntimeError("Placement-drive resolution returned no drive.")

        message.placement_drive_id = placement_drive.id
        db.flush()

        store_extracted_information(
            db=db,
            placement_drive_id=placement_drive.id,
            information=extracted,
            source_message_id=message.id,
        )

        message.processed = True
        db.commit()

        return {
            "message_id": message.id,
            "processed": True,
            "placement_drive_id": placement_drive.id,
            "nlp_result": result,
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Failed processing RawMessage %s", message_id)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message_id": message_id,
                "processed": False,
                "error": "Message processing failed while linking or storing extracted data.",
            },
        ) from exc