import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import RawMessage, PlacementDrive
from schemas import RawMessageCreate, RawMessageResponse

from nlp.raw_message_processor import (
    RawMessageProcessingError,
    process_raw_message_record,
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
        source_chat_id=message.source_chat_id,
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
    reprocess: bool = False,
    db: Session = Depends(get_db)
):
    try:
        response = process_raw_message_record(
            db=db,
            raw_message_id=message_id,
            reprocess=reprocess,
        )
        db.commit()
        return response
    except LookupError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RawMessageProcessingError as exc:
        db.rollback()
        logger.warning(
            "Unable to process RawMessage %s (%s): %s",
            message_id,
            exc.status,
            exc,
        )
        raise HTTPException(
            status_code=exc.status_code,
            detail={
                "status": exc.status,
                "message_id": message_id,
                "processed": False,
                "error": str(exc),
            },
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Failed processing RawMessage %s: %s", message_id, exc)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "failed",
                "message_id": message_id,
                "processed": False,
                "error": str(exc),
            },
        ) from exc