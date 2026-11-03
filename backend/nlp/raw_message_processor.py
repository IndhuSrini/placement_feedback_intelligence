import re

from sqlalchemy.orm import Session

from models import Company, PlacementDrive, RawMessage
from nlp.extractor import normalize_company_name
from nlp.processor import process_message
from nlp.storage import (
    DriveMatchAmbiguous,
    get_or_create_placement_drive_for_message,
    normalize_job_role,
    store_extracted_information,
    validate_placement_drive_context,
)


class RawMessageProcessingError(ValueError):
    def __init__(self, message: str, status_code: int = 422, status: str = "failed"):
        super().__init__(message)
        self.status_code = status_code
        self.status = status


def _company_name_in_message(db: Session, message_text: str):
    matches = []
    for company in db.query(Company).order_by(Company.id).all():
        name = normalize_company_name(company.name)
        if not name:
            continue

        pattern = r"(?<![A-Za-z0-9])" + r"\s+".join(
            re.escape(part) for part in name.split()
        ) + r"(?![A-Za-z0-9])"
        if re.search(pattern, message_text, re.IGNORECASE):
            matches.append(company.name)

    if len(matches) > 1:
        raise RawMessageProcessingError(
            "More than one known company is mentioned; the message cannot be "
            "linked safely without an explicit company field.",
            status_code=409,
            status="ambiguous",
        )
    return matches[0] if matches else None


def resolve_company_name(db: Session, extracted_name, message_text: str):
    if extracted_name:
        normalized = normalize_company_name(str(extracted_name))
        if normalized:
            return normalized
    return _company_name_in_message(db, message_text)


def _linked_drive(db: Session, message: RawMessage):
    if message.placement_drive_id is None:
        return None

    drive = db.query(PlacementDrive).filter(
        PlacementDrive.id == message.placement_drive_id
    ).first()
    if drive is None:
        raise RawMessageProcessingError(
            "The explicitly linked placement drive does not exist."
        )
    return drive


def process_raw_message_record(
    db: Session,
    raw_message_id: int,
    reprocess: bool = False,
):
    message = (
        db.query(RawMessage)
        .with_for_update()
        .populate_existing()
        .filter(RawMessage.id == raw_message_id)
        .first()
    )
    if message is None:
        raise LookupError(f"RawMessage {raw_message_id} does not exist.")

    if message.processed and not reprocess:
        return {
            "message_id": message.id,
            "processed": True,
            "placement_drive_id": message.placement_drive_id,
            "nlp_result": None,
            "already_processed": True,
        }

    if not message.message_text or not message.message_text.strip():
        raise RawMessageProcessingError("The raw message has no text.")

    result = process_message(message.message_text)
    information = result.get("extracted_information") or {}
    drive = _linked_drive(db, message)
    extracted_company = resolve_company_name(
        db,
        information.get("company"),
        message.message_text,
    )

    if drive is not None:
        drive_company = db.query(Company).filter(
            Company.id == drive.company_id
        ).first()
        if drive_company is None:
            raise RawMessageProcessingError(
                f"Placement drive {drive.id} has no associated company."
            )
        normalized_extracted = normalize_company_name(extracted_company)
        normalized_drive_company = normalize_company_name(drive_company.name)
        if normalized_extracted and (
            normalized_extracted.casefold()
            != normalized_drive_company.casefold()
        ):
            raise RawMessageProcessingError(
                "The extracted company does not match the explicitly linked "
                "placement drive."
            )
        if not information.get("job_role"):
            information["job_role"] = None
        validate_placement_drive_context(
            db,
            drive,
            message.message_text,
            information,
        )
        resolved_company_name = drive_company.name
    else:
        if not extracted_company:
            raise RawMessageProcessingError(
                "Company not detected; no placement drive could be linked."
            )

        try:
            drive = get_or_create_placement_drive_for_message(
                db=db,
                company_name=extracted_company,
                message_text=message.message_text,
                information=information,
            )
        except DriveMatchAmbiguous as exc:
            raise RawMessageProcessingError(
                str(exc),
                status_code=409,
                status="ambiguous",
            ) from exc
        resolved_company_name = extracted_company

    if (
        information.get("job_role")
        and drive.job_role
        and normalize_job_role(information["job_role"])
        != normalize_job_role(drive.job_role)
    ):
        raise RawMessageProcessingError(
            f"Extracted role '{information['job_role']}' does not match "
            f"placement drive role '{drive.job_role}'."
        )

    message.placement_drive_id = drive.id
    db.flush()
    store_extracted_information(
        db=db,
        placement_drive_id=drive.id,
        information=information,
        source_message_id=message.id,
    )
    message.processed = True

    return {
        "message_id": message.id,
        "processed": True,
        "placement_drive_id": drive.id,
        "company": resolved_company_name,
        "nlp_result": result,
        "already_processed": False,
    }
