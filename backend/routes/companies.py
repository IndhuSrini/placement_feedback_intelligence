from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Company
from schemas import CompanyCreate, CompanyResponse


router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.post("/", response_model=CompanyResponse)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):

    new_company = Company(
        name=company.name,
        industry=company.industry,
        website=company.website
    )

    db.add(new_company)
    db.commit()
    db.refresh(new_company)

    return new_company


@router.get("/", response_model=list[CompanyResponse])
def get_companies(
    db: Session = Depends(get_db)
):

    companies = db.query(Company).all()

    return companies