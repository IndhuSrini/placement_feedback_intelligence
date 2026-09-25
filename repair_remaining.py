import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from database import SessionLocal
from models import RawMessage, Company, PlacementDrive
from nlp.processor import process_message
from nlp.storage import store_extracted_information
from nlp.extractor import normalize_company_name


FALLBACK_COMPANIES = {
    234: "Tech Mahindra",
    235: "Tech Mahindra",
    236: "Capgemini",
    251: "Infosys",
}


db = SessionLocal()

try:
    success = 0

    for message_id, fallback_company in FALLBACK_COMPANIES.items():

        message = (
            db.query(RawMessage)
            .filter(RawMessage.id == message_id)
            .first()
        )

        if not message:
            print(f"Message {message_id}: not found")
            continue

        print(f"\nProcessing RawMessage {message_id}...")
        print(f"  Fallback company: {fallback_company}")

        result = process_message(message.message_text)
        info = result.get("extracted_information", {}) or {}

        company_name = info.get("company") or fallback_company
        company_name = normalize_company_name(company_name)

        company = (
            db.query(Company)
            .filter(Company.name.ilike(company_name))
            .first()
        )

        if company is None:
            company = Company(name=company_name)
            db.add(company)
            db.flush()

        drive = (
            db.query(PlacementDrive)
            .filter(PlacementDrive.company_id == company.id)
            .order_by(PlacementDrive.id.desc())
            .first()
        )

        if drive is None:
            drive = PlacementDrive(company_id=company.id)
            db.add(drive)
            db.flush()

        message.placement_drive_id = drive.id

        store_extracted_information(
            db=db,
            placement_drive_id=drive.id,
            information=info,
            source_message_id=message.id,
        )

        message.processed = True
        db.commit()

        print(
            f"  ✓ Linked message {message_id} → "
            f"{company.name} → drive {drive.id}"
        )

        success += 1

    print("\n" + "=" * 50)
    print("FINAL TELEGRAM REPAIR SUMMARY")
    print("=" * 50)
    print(f"Successfully repaired: {success}")
    print(f"Remaining: {len(FALLBACK_COMPANIES) - success}")

finally:
    db.close()
