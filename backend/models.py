from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Date,
    Boolean,
    ForeignKey
)

from database import Base


# ============================================================
# COMPANY
# ============================================================

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        unique=True,
        nullable=False
    )

    industry = Column(String(100))

    website = Column(String(255))


# ============================================================
# PLACEMENT DRIVE
# ============================================================

class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )

    recruitment_date = Column(Date)

    year = Column(Integer)

    job_role = Column(String(150))

    number_of_rounds = Column(Integer)

    overall_difficulty = Column(String(50))


# ============================================================
# RAW TELEGRAM / SOURCE MESSAGE
# ============================================================

class RawMessage(Base):
    __tablename__ = "raw_messages"

    id = Column(Integer, primary_key=True, index=True)

    message_id = Column(String(100))

    source = Column(String(100))

    sender = Column(String(150))

    message_text = Column(
        Text,
        nullable=False
    )

    message_date = Column(Date)
    placement_drive_id = Column(
    Integer,
    ForeignKey("placement_drives.id"),
    nullable=True
    )
    processed = Column(
        Boolean,
        default=False
    )


# ============================================================
# ELIGIBILITY CRITERIA
# ============================================================

class EligibilityCriteria(Base):
    __tablename__ = "eligibility_criteria"

    id = Column(Integer, primary_key=True, index=True)

    placement_drive_id = Column(
        Integer,
        ForeignKey("placement_drives.id"),
        nullable=False
    )

    minimum_cgpa = Column(Float)

    maximum_backlogs = Column(Integer)

    branch_eligibility = Column(String(255))

    other_criteria = Column(Text)


# ============================================================
# RECRUITMENT ROUND
# ============================================================

class RecruitmentRound(Base):
    __tablename__ = "recruitment_rounds"

    id = Column(Integer, primary_key=True, index=True)

    placement_drive_id = Column(
        Integer,
        ForeignKey("placement_drives.id"),
        nullable=False
    )

    round_number = Column(Integer)

    round_type = Column(String(100))

    difficulty = Column(String(50))

    description = Column(Text)


# ============================================================
# TOPIC
# ============================================================

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False
    )

    category = Column(String(100))


# ============================================================
# QUESTION
# ============================================================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    placement_drive_id = Column(
        Integer,
        ForeignKey("placement_drives.id"),
        nullable=True
    )

    round_id = Column(
        Integer,
        ForeignKey("recruitment_rounds.id"),
        nullable=True
    )

    topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=True
    )
    source_message_id = Column(
        Integer,
        ForeignKey("raw_messages.id"),
        nullable=True
    )

    question_text = Column(
        Text,
        nullable=False
    )

    difficulty = Column(String(50))

    occurrence_count = Column(
        Integer,
        default=1
    )

    # NEW: reliability / confidence
    confidence_score = Column(
        Float,
        default=35.0
    )

    # NEW: faculty verification status
    verification_status = Column(
        String(50),
        default="unverified"
    )


# ============================================================
# STUDENT EXPERIENCE
# ============================================================

class Experience(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)

    placement_drive_id = Column(
        Integer,
        ForeignKey("placement_drives.id"),
        nullable=True
    )

    experience_text = Column(Text)

    sentiment = Column(String(50))

    difficulty_rating = Column(Float)

    verified = Column(
        Boolean,
        default=False
    )


# ============================================================
# VERIFICATION RECORD
# ============================================================

class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)

    entity_type = Column(String(100))

    entity_id = Column(Integer)

    verified = Column(
        Boolean,
        default=False
    )

    confidence_score = Column(Float)

    verified_by = Column(String(150), nullable=True)

    notes = Column(Text, nullable=True)