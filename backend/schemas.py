from pydantic import BaseModel
from typing import Optional
from datetime import date


# -------------------------
# Company Schemas
# -------------------------

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------
# Placement Drive Schemas
# -------------------------

class PlacementDriveCreate(BaseModel):
    company_id: int
    recruitment_date: Optional[date] = None
    year: Optional[int] = None
    job_role: Optional[str] = None
    number_of_rounds: Optional[int] = None
    overall_difficulty: Optional[str] = None


class PlacementDriveResponse(BaseModel):
    id: int
    company_id: int
    recruitment_date: Optional[date] = None
    year: Optional[int] = None
    job_role: Optional[str] = None
    number_of_rounds: Optional[int] = None
    overall_difficulty: Optional[str] = None

    class Config:
        from_attributes = True


# -------------------------
# Raw Message Schemas
# -------------------------

class RawMessageCreate(BaseModel):
    message_id: Optional[str] = None
    source: Optional[str] = None
    sender: Optional[str] = None
    message_text: str
    message_date: Optional[date] = None

    # NEW
    placement_drive_id: Optional[int] = None


class RawMessageResponse(BaseModel):
    id: int
    message_id: Optional[str] = None
    source: Optional[str] = None
    sender: Optional[str] = None
    message_text: str
    message_date: Optional[date] = None
    processed: bool

    # NEW
    placement_drive_id: Optional[int] = None

    class Config:
        from_attributes = True