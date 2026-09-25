import sys

sys.path.insert(0, "backend")

from database import SessionLocal
from models import RawMessage, PlacementDrive, Company


db = SessionLocal()

try:
    print("\n--- TELEGRAM MESSAGES ---")

    rows = (
        db.query(RawMessage)
        .filter(RawMessage.source.ilike("telegram"))
        .order_by(RawMessage.id.desc())
        .limit(25)
        .all()
    )

    for r in rows:
        text = (r.message_text or "").replace("\n", " ")[:150]

        print(
            f"RawMessage ID={r.id} | "
            f"drive_id={r.placement_drive_id} | "
            f"processed={r.processed} | "
            f"text={text}"
        )

    print("\n--- PLACEMENT DRIVES ---")

    drives = (
        db.query(PlacementDrive)
        .order_by(PlacementDrive.id)
        .all()
    )

    for d in drives:
        company = (
            db.query(Company)
            .filter(Company.id == d.company_id)
            .first()
        )

        company_name = company.name if company else "?"

        print(
            f"Drive ID={d.id} | "
            f"company_id={d.company_id} | "
            f"company={company_name} | "
            f"role={d.job_role} | "
            f"rounds={d.number_of_rounds} | "
            f"difficulty={d.overall_difficulty}"
        )

finally:
    db.close()