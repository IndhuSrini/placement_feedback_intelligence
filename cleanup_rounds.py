import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from database import SessionLocal
from models import Company, PlacementDrive, RecruitmentRound, Question


db = SessionLocal()

try:
    print("=" * 60)
    print("SAFE ROUND CLEANUP")
    print("=" * 60)

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

        seen = {}

        for r in rounds:

            key = (
                (r.round_type or "").strip().lower(),
                (r.description or "").strip().lower(),
            )

            if key not in seen:
                seen[key] = r
                continue

            original = seen[key]

            # Check whether questions reference either round
            original_questions = db.query(Question).filter(
                Question.round_id == original.id
            ).count()

            duplicate_questions = db.query(Question).filter(
                Question.round_id == r.id
            ).count()

            # Keep the round that has questions attached
            if duplicate_questions > 0 and original_questions == 0:
                seen[key] = r
                db.delete(original)
                removed += 1

            elif duplicate_questions == 0:
                db.delete(r)
                removed += 1

            else:
                # Both contain questions.
                # Keep both rather than breaking question references.
                unique_key = (key, r.id)
                seen[unique_key] = r

        db.flush()

        # Reload remaining rounds
        remaining = (
            db.query(RecruitmentRound)
            .filter(
                RecruitmentRound.placement_drive_id == drive.id
            )
            .order_by(RecruitmentRound.id)
            .all()
        )

        # Give clean sequential numbers
        for index, r in enumerate(remaining, start=1):
            r.round_number = index

        drive.number_of_rounds = len(remaining)

    db.commit()

    print(f"\n✓ Duplicate unreferenced rounds removed: {removed}")

    print("\n" + "=" * 60)
    print("FINAL ROUND SUMMARY")
    print("=" * 60)

    drives = (
        db.query(PlacementDrive)
        .order_by(PlacementDrive.id)
        .all()
    )

    for drive in drives:

        company = (
            db.query(Company)
            .filter(Company.id == drive.company_id)
            .first()
        )

        name = company.name if company else "?"

        rounds = (
            db.query(RecruitmentRound)
            .filter(
                RecruitmentRound.placement_drive_id == drive.id
            )
            .order_by(RecruitmentRound.round_number)
            .all()
        )

        print(f"\n{name} | Drive {drive.id} | {len(rounds)} rounds")

        for r in rounds:
            question_count = db.query(Question).filter(
                Question.round_id == r.id
            ).count()

            print(
                f"  {r.round_number}. "
                f"{r.round_type} - "
                f"{r.description} "
                f"[{question_count} questions]"
            )

    print("\n" + "=" * 60)
    print("SAFE CLEANUP COMPLETE")
    print("=" * 60)

finally:
    db.close()
