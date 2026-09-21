from __future__ import annotations

import asyncio
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from telegram.client import (
    TelegramChatIdError,
    TelegramConfigError,
    TelegramConnectionError,
    create_client,
    get_authorized_chat_ids,
)

TARGET_CHAT_ID = -5460633687
BATCH = "2023-27 batch"
COMPANIES = [
    "TCS",
    "Infosys",
    "Cognizant",
    "Accenture",
    "Capgemini",
    "Wipro",
    "Zoho",
    "Freshworks",
    "HCLTech",
    "IBM",
    "Tech Mahindra",
    "Deloitte",
]
ROLES = [
    "Software Engineer",
    "Graduate Engineer Trainee",
    "Programmer Analyst",
    "Software Developer",
    "Associate Software Engineer",
    "System Engineer",
    "Java Developer",
    "Python Developer",
]
CGPA_VALUES = ["6.5 CGPA", "7 CGPA", "7.5 CGPA", "8 CGPA"]
BACKLOG_RULES = [
    "no active backlogs",
    "no standing arrears",
    "no active backlogs and no standing arrears",
    "no active backlogs; no standing arrears",
    "eligible only with no active backlogs",
    "eligible only with no standing arrears",
]
ROUNDS = [
    "Aptitude",
    "Coding",
    "Communication",
    "Technical Interview",
    "Managerial Interview",
    "HR",
]
DIFFICULTY = ["Easy", "Medium", "Moderate", "Hard"]
TOPICS = [
    "DBMS",
    "Normalization",
    "SQL",
    "OOP",
    "Java",
    "Python",
    "Operating Systems",
    "Process vs Thread",
    "Computer Networks",
    "Data Structures",
    "Arrays",
    "Strings",
    "Stacks",
    "Queues",
]
QUESTION_BANK = [
    "Explain normalization in DBMS",
    "Difference between process and thread",
    "Explain inheritance",
    "What is polymorphism?",
    "Write SQL query to find second highest salary",
    "Reverse a string",
    "Write a program to reverse a given string",
    "Asked to reverse the input string",
    "Find duplicate elements in an array",
    "Find maximum/minimum in an array",
    "Check palindrome",
    "Explain primary key and foreign key",
    "Explain JOINs",
    "Difference between abstract class and interface",
    "Explain exception handling",
    "Explain stack and queue",
    "Write code to reverse a string in Java",
    "Explain SQL normalization with examples",
    "What is the difference between process and thread in OS?",
    "How do you handle inheritance and polymorphism in OOP?",
    "Find the second highest salary using SQL",
]
RECRUITMENT_DATES = [
    "2026-01-12",
    "2026-02-03",
    "2026-02-18",
    "2026-03-11",
    "2026-03-24",
    "2026-04-09",
    "2026-04-27",
    "2026-05-13",
    "2026-05-28",
    "2026-06-17",
    "2026-07-02",
    "2026-07-21",
    "2026-08-09",
    "2026-08-25",
    "2026-09-14",
    "2026-10-05",
    "2026-10-22",
    "2026-11-11",
    "2026-11-29",
    "2026-12-16",
]


def _get_configured_chat_ids() -> List[int]:
    load_dotenv(BACKEND_DIR / ".env")
    return get_authorized_chat_ids()


def _validate_target_chat() -> int:
    configured_ids = _get_configured_chat_ids()
    if len(configured_ids) != 1 or configured_ids[0] != TARGET_CHAT_ID:
        raise TelegramChatIdError(
            f"Refusing to send: TELEGRAM_CHAT_IDS must be exactly [{TARGET_CHAT_ID}] for the private TEST group. "
            f"Current value: {configured_ids}"
        )
    return configured_ids[0]


def _pick_rounds(rng: random.Random) -> str:
    count = rng.choice([2, 3, 4, 5, 6])
    selected = rng.sample(ROUNDS, k=count)
    return ", ".join(selected)


def _pick_eligibility(rng: random.Random) -> str:
    cgpa = rng.choice(CGPA_VALUES)
    backlogs = rng.choice(BACKLOG_RULES)
    return f"{cgpa}; {backlogs}"


def _pick_questions(rng: random.Random, count: int = 2) -> str:
    selected = rng.sample(QUESTION_BANK, k=min(count, len(QUESTION_BANK)))
    return "; ".join(selected)


def _pick_topics(rng: random.Random, count: int = 3) -> str:
    selected = rng.sample(TOPICS, k=min(count, len(TOPICS)))
    return ", ".join(selected)


def _pick_company(rng: random.Random) -> str:
    return rng.choice(COMPANIES)


def _pick_role(rng: random.Random) -> str:
    return rng.choice(ROLES)


def _pick_date(rng: random.Random) -> str:
    return rng.choice(RECRUITMENT_DATES)


def _build_structured_message(rng: random.Random) -> str:
    company = _pick_company(rng)
    role = _pick_role(rng)
    eligibility = _pick_eligibility(rng)
    rounds = _pick_rounds(rng)
    difficulty = rng.choice(DIFFICULTY)
    date = _pick_date(rng)
    topic_text = _pick_topics(rng, 3)
    question_text = _pick_questions(rng, 2)
    sentence_bank = [
        f"Placement update: {company} is hiring for {role} in the {BATCH}.",
        f"Eligibility: {eligibility}.",
        f"Interview flow: {rounds}.",
        f"Difficulty: {difficulty}.",
        f"Recruitment date: {date}.",
        f"Focus topics: {topic_text}.",
        f"Questions discussed: {question_text}.",
    ]
    return " ".join(rng.sample(sentence_bank, k=len(sentence_bank)))


def _build_experience_message(rng: random.Random) -> str:
    company = _pick_company(rng)
    role = _pick_role(rng)
    rounds = _pick_rounds(rng)
    difficulty = rng.choice(DIFFICULTY)
    if rng.random() < 0.5:
        company = ""
    if rng.random() < 0.6:
        eligibility = _pick_eligibility(rng)
    else:
        eligibility = ""
    question_text = _pick_questions(rng, 3)
    topic_text = _pick_topics(rng, 2)
    parts = [
        f"Interview experience for {company} {role} drive" if company else "Interview experience",
        f"for the {BATCH}",
        f"had rounds: {rounds}.",
        f"Difficulty was {difficulty}.",
    ]
    if eligibility:
        parts.append(f"Eligibility: {eligibility}.")
    parts.append(f"Question pattern: {question_text}.")
    parts.append(f"Core topics: {topic_text}.")
    return " ".join(parts)


def _build_short_update(rng: random.Random) -> str:
    company = rng.choice(COMPANIES) if rng.random() < 0.8 else ""
    role = rng.choice(ROLES) if rng.random() < 0.8 else ""
    overview = []
    if company:
        overview.append(company)
    if role:
        overview.append(role)
    if overview:
        prefix = " ".join(overview)
    else:
        prefix = "Drive"
    segments = [
        f"{prefix} update for {BATCH}.",
        f"Eligibility: {_pick_eligibility(rng)}.",
        f"Rounds: {_pick_rounds(rng)}.",
        f"Difficulty: {rng.choice(DIFFICULTY)}.",
        f"Q: {_pick_questions(rng, 1)}.",
    ]
    return " ".join(rng.sample(segments, k=len(segments)))


def _build_informal_message(rng: random.Random) -> str:
    company = _pick_company(rng) if rng.random() < 0.75 else ""
    role = _pick_role(rng) if rng.random() < 0.7 else ""
    if company and role:
        subject = f"{company} {role} drive"
    elif company:
        subject = f"{company} drive"
    elif role:
        subject = f"{role} drive"
    else:
        subject = "Drive"

    lines = [
        f"yo guys, {subject} for {BATCH} seems okay.",
        f"Elig: {_pick_eligibility(rng)}.",
        f"Rounds: {_pick_rounds(rng)}.",
        f"Apti and coding were the tough ones; communication was fine.",
        f"Topic focus: {_pick_topics(rng, 2)}.",
    ]
    if rng.random() < 0.5:
        lines.append(f"Question asked: {_pick_questions(rng, 1)}.")
    return " ".join(lines)


def _build_bullet_message(rng: random.Random) -> str:
    company = _pick_company(rng) if rng.random() < 0.8 else ""
    role = _pick_role(rng) if rng.random() < 0.8 else ""
    lines = ["- Placement summary", f"- Batch: {BATCH}"]
    if company:
        lines.append(f"- Company: {company}")
    if role:
        lines.append(f"- Role: {role}")
    lines.append(f"- Eligibility: {_pick_eligibility(rng)}")
    lines.append(f"- Rounds: {_pick_rounds(rng)}")
    lines.append(f"- Difficulty: {rng.choice(DIFFICULTY)}")
    lines.append(f"- Topics: {_pick_topics(rng, 3)}")
    lines.append(f"- Questions: {_pick_questions(rng, 2)}")
    return "\n".join(lines)


def _build_numbered_message(rng: random.Random) -> str:
    company = _pick_company(rng) if rng.random() < 0.8 else ""
    lines = ["1. Placement update"]
    if company:
        lines.append(f"2. Company: {company}")
    else:
        lines.append("2. Company: not mentioned")
    lines.append(f"3. Batch: {BATCH}")
    lines.append(f"4. Role: {_pick_role(rng)}")
    lines.append(f"5. Eligibility: {_pick_eligibility(rng)}")
    lines.append(f"6. Round flow: {_pick_rounds(rng)}")
    lines.append(f"7. Topic review: {_pick_topics(rng, 3)}")
    lines.append(f"8. Sample Q: {_pick_questions(rng, 1)}")
    return "\n".join(lines)


def _build_abbreviated_message(rng: random.Random) -> str:
    company = _pick_company(rng)
    role = _pick_role(rng)
    if rng.random() < 0.6:
        company = ""
    pieces = [
        f"{BATCH}",
        f"{company or 'drive'}",
        f"{role or 'role'}",
        "elig: " + _pick_eligibility(rng),
        "rnds: " + _pick_rounds(rng),
        "diff: " + rng.choice(DIFFICULTY),
        "q: " + _pick_questions(rng, 1),
        "topic: " + _pick_topics(rng, 2),
    ]
    return " | ".join(pieces)


def _build_multisentence_message(rng: random.Random) -> str:
    company = _pick_company(rng) if rng.random() < 0.75 else ""
    role = _pick_role(rng) if rng.random() < 0.8 else ""
    sentences = [f"Recruitment for the {BATCH} is active."]
    if company:
        sentences.append(f"{company} posted a {role or 'technical'} role update.")
    else:
        sentences.append(f"A technical role update came in for the {BATCH}.")
    sentences.append(f"Eligibility requirement was {_pick_eligibility(rng)}.")
    sentences.append(f"The interview sequence was {_pick_rounds(rng)}.")
    sentences.append(f"The difficulty was {rng.choice(DIFFICULTY)}.")
    sentences.append(f"The recurring question was {_pick_questions(rng, 1)}.")
    sentences.append(f"Topics revisited included {_pick_topics(rng, 2)}.")
    return " ".join(sentences)


def _build_rounds_only_message(rng: random.Random) -> str:
    return f"Round flow: {_pick_rounds(rng)}. Batch: {BATCH}."


def _build_eligibility_only_message(rng: random.Random) -> str:
    return f"Eligibility: {_pick_eligibility(rng)}. Batch: {BATCH}."


def _build_question_only_message(rng: random.Random) -> str:
    question = _pick_questions(rng, 1)
    return f"Question asked: {question}."


def _build_message(rng: random.Random, index: int) -> str:
    style = rng.choices(
        [
            "structured",
            "experience",
            "short",
            "informal",
            "bullet",
            "numbered",
            "abbrev",
            "multisentence",
            "rounds_only",
            "eligibility_only",
            "question_only",
        ],
        weights=[18, 16, 12, 12, 10, 8, 8, 8, 4, 3, 11],
        k=1,
    )[0]

    if style == "structured":
        message = _build_structured_message(rng)
    elif style == "experience":
        message = _build_experience_message(rng)
    elif style == "short":
        message = _build_short_update(rng)
    elif style == "informal":
        message = _build_informal_message(rng)
    elif style == "bullet":
        message = _build_bullet_message(rng)
    elif style == "numbered":
        message = _build_numbered_message(rng)
    elif style == "abbrev":
        message = _build_abbreviated_message(rng)
    elif style == "multisentence":
        message = _build_multisentence_message(rng)
    elif style == "rounds_only":
        message = _build_rounds_only_message(rng)
    elif style == "eligibility_only":
        message = _build_eligibility_only_message(rng)
    else:
        message = _build_question_only_message(rng)

    if index % 10 == 0:
        message = message + f" Recruitment date: {_pick_date(rng)}."

    return message


def generate_messages(count: int = 200, seed: int = 2026) -> List[str]:
    rng = random.Random(seed)
    messages: List[str] = []
    for index in range(1, count + 1):
        text = _build_message(rng, index)
        messages.append(text)
    return messages


async def send_messages(messages: List[str], delay_seconds: float = 0.8) -> Tuple[int, int]:
    client = create_client()
    sent_count = 0
    failed_count = 0

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.start()

        target_chat_id = _validate_target_chat()
        entity = await client.get_entity(target_chat_id)
        if entity is None:
            raise TelegramConnectionError(f"Cannot resolve Telegram chat {target_chat_id}.")

        for position, message in enumerate(messages, start=1):
            try:
                await client.send_message(entity, message)
                sent_count += 1
                print(f"Sent {position}/{len(messages)}")
            except Exception as exc:
                failed_count += 1
                print(f"Failed {position}/{len(messages)}: {exc}")
            if position < len(messages):
                time.sleep(delay_seconds)

        return sent_count, failed_count
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


async def main() -> None:
    print("Preparing synthetic Telegram placement test messages...")
    messages = generate_messages(count=200)
    total_generated = len(messages)
    print(f"Total generated: {total_generated}")

    try:
        _validate_target_chat()
    except (TelegramConfigError, TelegramChatIdError, ValueError) as exc:
        print(f"Refusing to send: {exc}")
        return

    print(f"Target chat ID: {TARGET_CHAT_ID}")
    print("Sending synthetic messages to the configured private TEST group...")
    sent_count, failed_count = await send_messages(messages, delay_seconds=0.8)
    print("Final summary")
    print(f"Total generated: {total_generated}")
    print(f"Total sent: {sent_count}")
    print(f"Failed: {failed_count}")


if __name__ == "__main__":
    asyncio.run(main())
