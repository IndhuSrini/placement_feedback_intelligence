import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from database import SessionLocal
from models import (
    Company,
    PlacementDrive,
    RawMessage,
    EligibilityCriteria,
    RecruitmentRound,
    Question,
    Experience,
)


db = SessionLocal()

try:
    print("=" * 60)
    print("DATABASE CLEANUP")
    print("=" * 60)

    # ---------------------------------------------------------
    # REMOVE UNKNOWN COMPANY AND ITS DRIVE
    # ---------------------------------------------------------

    unknown = (
        db.query(Company)
        .filter(Company.name.ilike("Unknown Company"))
        .first()
    )

    if unknown:
        print(f"\nRemoving Unknown Company ID: {unknown.id}")

        drives = (
            db.query(PlacementDrive)
            .filter(PlacementDrive.company_id == unknown.id)
            .all()
        )

        for drive in drives:
            print(f"Removing drive {drive.id}")

            db.query(Question).filter(
                Question.placement_drive_id == drive.id
            ).delete(synchronize_session=False)

            db.query(RecruitmentRound).filter(
                RecruitmentRound.placement_drive_id == drive.id
            ).delete(synchronize_session=False)

            db.query(EligibilityCriteria).filter(
                EligibilityCriteria.placement_drive_id == drive.id
            ).delete(synchronize_session=False)

            db.query(Experience).filter(
                Experience.placement_drive_id == drive.id
            ).delete(synchronize_session=False)

            db.query(RawMessage).filter(
                RawMessage.placement_drive_id == drive.id
            ).update(
                {
                    RawMessage.placement_drive_id: None,
                    RawMessage.processed: False,
                },
                synchronize_session=False,
            )

            db.delete(drive)

        db.flush()

        db.delete(unknown)
        db.commit()

        print("✓ Unknown Company removed")
    else:
        print("\nUnknown Company already removed")

    # ---------------------------------------------------------
    # CLEAN EXACT DUPLICATE ROUNDS
    # ---------------------------------------------------------

    print("\nCleaning duplicate rounds...")

    drives = (
        db.query(PlacementDrive)
        .order_by(PlacementDrive.id)
        .all()
    )

    removed = 0

    for drive in drives:

        rounds = (
            db.query(RecruitmentRound)
            .filter(
                RecruitmentRound.placement_drive_id == drive.id
            )
            .order_by(RecruitmentRound.id)
            .all()
        )

        seen = set()
        keep = []

        for r in rounds:

            key = (
                (r.round_type or "").strip().lower(),
                (r.description or "").strip().lower(),
            )

            if key in seen:
                db.delete(r)
                removed += 1
            else:
                seen.add(key)
                keep.append(r)

        db.flush()

        for index, r in enumerate(keep, start=1):
            r.round_number = index

        drive.number_of_rounds = len(keep)

    db.commit()

    print(f"✓ Duplicate rounds removed: {removed}")

    # ---------------------------------------------------------
    # FINAL SUMMARY
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL COMPANIES")
    print("=" * 60)

    companies = (
        db.query(Company)
        .order_by(Company.id)
        .all()
    )

    for company in companies:
        print(f"{company.id}. {company.name}")

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

finally:
    db.close()
