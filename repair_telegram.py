import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import SessionLocal
from models import RawMessage, Company, PlacementDrive
from nlp.processor import process_message
from nlp.storage import store_extracted_information
from nlp.extractor import normalize_company_name


db = SessionLocal()

try:
    messages = (
        db.query(RawMessage)
        .filter(
            RawMessage.source.ilike("telegram"),
            RawMessage.processed == False,
            RawMessage.placement_drive_id == None,
            RawMessage.message_text != "Hi",
        )
        .order_by(RawMessage.id)
        .all()
    )

    print(f"Messages selected for repair: {len(messages)}")
    print("-" * 50)

    success = 0
    failure = 0

    for message in messages:
        try:
            print(f"\nProcessing RawMessage {message.id}...")

            result = process_message(message.message_text)
            info = result.get("extracted_information", {}) or {}

            company_name = info.get("company")

            if not company_name:
                print("  Company not detected - skipped")
                failure += 1
                continue

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
                print(f"  Created company: {company.name}")
            else:
                print(f"  Company: {company.name}")

            drive = (
                db.query(PlacementDrive)
                .filter(PlacementDrive.company_id == company.id)
                .order_by(PlacementDrive.id.desc())
                .first()
            )

            if drive is None:
                drive = PlacementDrive(
                    company_id=company.id
                )
                db.add(drive)
                db.flush()
                print(f"  Created drive: {drive.id}")
            else:
                print(f"  Using existing drive: {drive.id}")

            message.placement_drive_id = drive.id

            store_extracted_information(
                db=db,
                placement_drive_id=drive.id,
                information=info,
                source_message_id=message.id,
            )

            message.processed = True

            db.commit()

            print(f"  ✓ Linked message {message.id} → {company.name} → drive {drive.id}")
            success += 1

        except Exception as exc:
            db.rollback()
            print(f"  ✗ Failed: {exc}")
            failure += 1

    print("\n" + "=" * 50)
    print("TELEGRAM REPAIR SUMMARY")
    print("=" * 50)
    print(f"Messages selected: {len(messages)}")
    print(f"Successfully processed: {success}")
    print(f"Failed: {failure}")

finally:
    db.close()
