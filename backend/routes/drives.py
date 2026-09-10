from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import PlacementDrive, Company
from schemas import PlacementDriveCreate, PlacementDriveResponse


router = APIRouter(
    prefix="/placement-drives",
    tags=["Placement Drives"]
)


@router.post("/", response_model=PlacementDriveResponse)
def create_placement_drive(
    drive: PlacementDriveCreate,
    db: Session = Depends(get_db)
):

    company = db.query(Company).filter(
        Company.id == drive.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    new_drive = PlacementDrive(
        company_id=drive.company_id,
        recruitment_date=drive.recruitment_date,
        year=drive.year,
        job_role=drive.job_role,
        number_of_rounds=drive.number_of_rounds,
        overall_difficulty=drive.overall_difficulty
    )

    db.add(new_drive)
    db.commit()
    db.refresh(new_drive)

    return new_drive


@router.get("/", response_model=list[PlacementDriveResponse])
def get_placement_drives(
    db: Session = Depends(get_db)
):

    drives = db.query(PlacementDrive).all()

    return drives