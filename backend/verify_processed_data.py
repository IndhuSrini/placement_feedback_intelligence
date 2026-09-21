from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

from database import SessionLocal
from models import Company, EligibilityCriteria, PlacementDrive, Question, RawMessage, RecruitmentRound, Topic


def main() -> None:
    db = SessionLocal()

    try:
        total_raw_messages = db.query(RawMessage).count()
        processed_raw_messages = db.query(RawMessage).filter(RawMessage.processed.is_(True)).count()
        unprocessed_raw_messages = db.query(RawMessage).filter(RawMessage.processed.is_(False)).count()

        total_companies = db.query(Company).count()
        total_drives = db.query(PlacementDrive).count()
        total_eligibility = db.query(EligibilityCriteria).count()
        total_rounds = db.query(RecruitmentRound).count()
        total_questions = db.query(Question).count()
        total_topics = db.query(Topic).count()

        telegram_processed = db.query(RawMessage).filter(RawMessage.source == "telegram", RawMessage.processed.is_(True)).count()
        telegram_unprocessed = db.query(RawMessage).filter(RawMessage.source == "telegram", RawMessage.processed.is_(False)).count()

        print("Database verification summary")
        print(f"total RawMessage records: {total_raw_messages}")
        print(f"processed RawMessage records: {processed_raw_messages}")
        print(f"unprocessed RawMessage records: {unprocessed_raw_messages}")
        print(f"total Companies: {total_companies}")
        print(f"total PlacementDrives: {total_drives}")
        print(f"total EligibilityCriteria records: {total_eligibility}")
        print(f"total RecruitmentRounds: {total_rounds}")
        print(f"total Questions: {total_questions}")
        print(f"total Topics: {total_topics}")
        print(f"Telegram RawMessages with processed=True: {telegram_processed}")
        print(f"Telegram RawMessages with processed=False: {telegram_unprocessed}")

        print("Sample processed RawMessages")
        sample_messages = (
            db.query(RawMessage)
            .filter(RawMessage.processed.is_(True))
            .order_by(RawMessage.id.asc())
            .limit(10)
            .all()
        )

        if not sample_messages:
            print("No processed RawMessage records found.")
        else:
            for message in sample_messages:
                print(f"message ID: {message.id} | placement_drive_id: {message.placement_drive_id} | processed: {message.processed}")

        print("Sample Questions")
        sample_questions = (
            db.query(Question)
            .order_by(Question.id.asc())
            .limit(10)
            .all()
        )

        if not sample_questions:
            print("No Question records found.")
        else:
            for question in sample_questions:
                topic_name = None
                if question.topic_id is not None:
                    topic = db.query(Topic).filter(Topic.id == question.topic_id).first()
                    if topic is not None:
                        topic_name = topic.name

                round_name = None
                if question.round_id is not None:
                    round_record = db.query(RecruitmentRound).filter(RecruitmentRound.id == question.round_id).first()
                    if round_record is not None:
                        round_name = round_record.round_type

                print(f"question text: {question.question_text} | topic: {topic_name} | recruitment round: {round_name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
