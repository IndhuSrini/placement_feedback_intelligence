from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import RawMessage, PlacementDrive
from schemas import RawMessageCreate, RawMessageResponse

from nlp.processor import process_message
from nlp.storage import store_extracted_information


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
    # Validate placement drive if provided
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

    # --------------------------------------------------------
    # Check placement drive
    # --------------------------------------------------------

    if message.placement_drive_id is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "This message is not associated with a "
                "placement drive. Please provide "
                "placement_drive_id first."
            )
        )

    # --------------------------------------------------------
    # Find the correct placement drive
    # --------------------------------------------------------

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
    # Run NLP processing
    # --------------------------------------------------------

    result = process_message(
        message.message_text
    )

    # --------------------------------------------------------
    # Store extracted information
    # --------------------------------------------------------

    store_extracted_information(
        db=db,
        placement_drive_id=placement_drive.id,
        information=result["extracted_information"],
        source_message_id=message.id
    )

    # --------------------------------------------------------
    # Mark message as processed
    # --------------------------------------------------------

    message.processed = True

    db.commit()

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "message_id": message.id,
        "processed": True,
        "placement_drive_id": placement_drive.id,
        "nlp_result": result
    }