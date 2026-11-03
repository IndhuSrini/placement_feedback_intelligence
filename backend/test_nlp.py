import re

from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from database import Base
from models import (
    Company,
    EligibilityCriteria,
    EligibilitySourceMessage,
    Experience,
    PlacementDrive,
    PlacementDriveTopic,
    Question,
    QuestionSourceMessage,
    PlacementDriveTopicSourceMessage,
    RawMessage,
    RecruitmentRound,
    RecruitmentRoundSourceMessage,
    Topic,
)
from nlp.cleaner import clean_message
from nlp.classifier import classify_message
from nlp.duplicate_detector import calculate_similarity, is_duplicate
from nlp.extractor import extract_information, extract_questions
from nlp.storage import (
    DriveMatchAmbiguous,
    get_or_create_placement_drive_for_message,
    infer_job_role_from_message,
    store_extracted_information,
)
from reprocess_messages import inspect_message
from routes.analytics import company_analytics, frequent_questions, frequent_topics
from routes.messages import process_raw_message


@pytest.mark.parametrize(
    "text,expected_cgpa,expected_backlogs,expected_rounds,expected_categories",
    [
        (
            "TCS eligibility is 7 CGPA with no active backlogs. First round aptitude and second round coding.",
            7.0,
            0,
            [(1, "Aptitude"), (2, "Coding")],
            ["Eligibility", "Aptitude", "Coding"],
        ),
        (
            "2nd round technical interview was hard.",
            None,
            None,
            [(2, "Technical")],
            ["Technical"],
        ),
    ],
)
def test_round_and_eligibility_extraction(text, expected_cgpa, expected_backlogs, expected_rounds, expected_categories):
    cleaned = clean_message(text)
    categories = classify_message(cleaned)
    information = extract_information(cleaned)

    assert information["minimum_cgpa"] == expected_cgpa
    assert information["maximum_backlogs"] == expected_backlogs

    observed_rounds = [
        (round_info["round_number"], round_info["round_type"])
        for round_info in information["rounds"]
    ]
    assert observed_rounds == expected_rounds

    for category in expected_categories:
        assert category in categories


def test_difficulty_is_assigned_to_the_round_it_describes():
    info = extract_information(
        clean_message(
            "Company: Difficulty Mapping Co\n"
            "Round 1: Coding\n"
            "Difficulty: Easy\n"
            "Coding topics: Arrays\n"
            "Question: Find the frequency of each element in an array.\n"
            "Round 2: Aptitude\n"
            "Difficulty: Hard\n"
            "Aptitude topics: Probability\n"
            "Question: What is the probability of drawing a red card?"
        )
    )

    question_difficulties = {
        detail["category"]: detail["difficulty"]
        for detail in info["question_details"]
    }
    round_difficulties = {
        detail["round_type"]: detail["difficulty"]
        for detail in info["rounds"]
    }
    assert question_difficulties == {"Coding": "Easy", "Aptitude": "Hard"}
    assert round_difficulties == {"Coding": "Easy", "Aptitude": "Hard"}


def test_technical_question_and_topic_extraction():
    text = "Technical interview asked explain normalization in DBMS and difference between process and thread."
    information = extract_information(clean_message(text))

    assert "Technical" in classify_message(clean_message(text))
    assert "DBMS" in information["topics"]
    assert any(topic in {"Operating System", "Process", "Thread"} for topic in information["topics"])
    assert any("normalization" in question.lower() or "process" in question.lower() for question in information["questions"])


def test_coding_question_and_difficulty_extraction():
    text = "Asked to reverse a string and find duplicate elements in an array. Coding round was medium difficulty."
    information = extract_information(clean_message(text))

    assert "Coding" in classify_message(clean_message(text))
    assert "Strings" in information["topics"]
    assert "Arrays" in information["topics"]
    assert any("reverse a string" in question.lower() or "duplicate elements" in question.lower() for question in information["questions"])
    assert "Medium" in information["difficulty"]


def test_hr_question_extraction():
    text = "HR asked tell me about yourself, strengths, weaknesses and are you willing to relocate?"
    information = extract_information(clean_message(text))

    assert "HR" in classify_message(clean_message(text))
    assert any("yourself" in question.lower() or "relocate" in question.lower() for question in information["questions"])


def test_cgpa_decimal_precision():
    text = "Candidate had 8.2 CGPA and no backlogs."
    information = extract_information(clean_message(text))

    assert information["minimum_cgpa"] == 8.2
    assert information["maximum_backlogs"] == 0


def test_hard_difficulty_mapping():
    text = "2nd round technical interview was hard."
    information = extract_information(clean_message(text))

    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] == 2 for round_info in information["rounds"])
    assert "Hard" in information["difficulty"]


def test_round_stage_deduplication_and_stage_detection():
    text = (
        "TCS eligibility is 7 CGPA with no active backlogs. "
        "First round aptitude and second round coding. "
        "Technical interview asked explain normalization in DBMS and difference between process and thread. "
        "Asked to reverse a string and find duplicate elements in an array. "
        "Coding round was medium difficulty. "
        "HR asked tell me about yourself, strengths, weaknesses and are you willing to relocate?"
    )
    information = extract_information(clean_message(text))

    rounds = information["rounds"]
    observed = [(round_info["round_number"], round_info["round_type"]) for round_info in rounds]
    assert (1, "Aptitude") in observed
    assert (2, "Coding") in observed
    assert any(item[1] == "Technical" for item in observed)
    assert any(item[1] == "HR" for item in observed)
    assert len([item for item in observed if item[1] == "Coding"]) == 1
    assert len([item for item in observed if item[1] == "Technical"]) == 1
    assert len([item for item in observed if item[1] == "HR"]) == 1
    assert all(item[0] is None for item in observed if item[1] in {"Technical", "HR"})


def test_difficulty_uses_word_boundaries_only():
    text = (
        "TCS eligibility is 7 CGPA with no active backlogs. "
        "First round aptitude and second round coding. "
        "Technical interview asked explain normalization in DBMS and difference between process and thread. "
        "Asked to reverse a string and find duplicate elements in an array. "
        "Coding round was medium difficulty. "
        "HR asked tell me about yourself, strengths, weaknesses and are you willing to relocate?"
    )
    information = extract_information(clean_message(text))

    assert information["difficulty"] == ["Medium"]


def test_question_extraction_prefers_atomic_questions_without_container_duplicates():
    text = (
        "Technical interview asked explain normalization in DBMS and difference between process and thread. "
        "Asked to reverse a string and find duplicate elements in an array. "
        "HR asked tell me about yourself, strengths, weaknesses and are you willing to relocate?"
    )
    information = extract_information(clean_message(text))
    questions = [q.lower() for q in information["questions"]]

    assert any("explain normalization in dbms" in q for q in questions)
    assert any("difference between process and thread" in q for q in questions)
    assert any("reverse a string" in q for q in questions)
    assert any("find duplicate elements in an array" in q for q in questions)
    assert any("tell me about yourself" in q for q in questions)
    assert any("are you willing to relocate" in q for q in questions)
    assert not any("and find duplicate elements in an array" in q for q in questions)
    assert not any("difference between process and thread and" in q for q in questions)
    assert not any("explain normalization in dbms and difference between process and thread" in q for q in questions)


def test_adjacent_question_splitting_discards_incomplete_fragments():
    text = (
        "What is a circuit?What is the? "
        "difference between AC and DC current?"
    )
    questions = extract_information(clean_message(text))["questions"]

    assert questions == [
        "What is a circuit?",
        "difference between AC and DC current?",
    ]
    assert extract_questions("What is the?") == []


def test_questions_discussed_heading_separates_questions_from_feedback():
    information = extract_information(
        clean_message(
            "Questions discussed:\n"
            "1. Explain method overloading and method overriding.\n"
            "2. Compare arrays and linked lists.\n"
            "Feedback: The interviewer was supportive."
        )
    )

    assert information["questions"] == [
        "Explain method overloading and method overriding?",
        "Compare arrays and linked lists?",
    ]
    assert information["feedback"] == ["The interviewer was supportive"]


@pytest.mark.parametrize(
    "fragment",
    [
        "What is the?",
        "How to",
        "Difference between?",
        "Explain your",
    ],
)
def test_incomplete_question_fragments_are_not_extracted(fragment):
    assert extract_questions(fragment) == []


def test_unpunctuated_adjacent_questions_are_extracted_separately():
    text = "Explain cloud resources Explain microservices vs monolithic?"
    questions = extract_information(clean_message(text))["questions"]

    assert questions == [
        "Explain cloud resources?",
        "Explain microservices vs monolithic?",
    ]


def test_coordinated_interview_prompts_are_stored_as_complete_questions():
    text = "Asked to reverse a string and find duplicate elements in an array."
    information = extract_information(clean_message(text))

    assert information["questions"] == [
        "reverse a string?",
        "find duplicate elements in an array?",
    ]

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Question Test Co")
    session.add(company)
    session.flush()
    drive = PlacementDrive(company_id=company.id)
    session.add(drive)
    session.flush()

    store_extracted_information(
        session,
        drive.id,
        information,
        source_message_id=None,
    )

    stored_questions = [
        question.question_text
        for question in session.query(Question)
        .filter_by(placement_drive_id=drive.id)
        .all()
    ]
    assert set(stored_questions) == set(information["questions"])

    session.close()


def test_duplicate_detection_ignores_shared_question_templates_and_fragments():
    assert calculate_similarity("What is OOP?", "What is OS?") == 0.0
    assert not is_duplicate(
        "What is the?",
        ["What is the purpose of a resistor in a circuit?"],
    )["duplicate"]
    assert calculate_similarity(
        "Explain differences between process and thread",
        "Difference between process and thread",
    ) == 1.0


def test_difficulty_requires_relevant_context_and_does_not_infer_defaults():
    assert extract_information(clean_message("Company: Mistral\nSelf intro"))["difficulty"] == []
    assert extract_information(clean_message("The hard disk was mentioned."))["difficulty"] == []
    assert extract_information(clean_message("The interview was not hard."))["difficulty"] == []
    assert extract_information(clean_message("The interview was hard."))["difficulty"] == ["Hard"]


def test_company_and_round_rule_regressions():
    info = extract_information(clean_message("Company: Infosys\nRound: Technical\nWhat is OOP?\nDifference between abstract class and interface?\nDifficulty: Medium\nInterview was friendly and mostly resume based."))

    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] is None for round_info in info["rounds"])
    assert "Medium" in info["difficulty"]
    assert any("friendly" in text.lower() or "resume" in text.lower() for text in info["feedback"])
    assert any("what is oop" in q.lower() for q in info["questions"])
    assert any("abstract class" in q.lower() for q in info["questions"])


@pytest.mark.parametrize(
    "text,expected_company",
    [
        ("company amazon", "Amazon"),
        ("Company Name: Zentropy", "Zentropy"),
        ("Company: LTIMindtree", "LTIMindtree"),
    ],
)
def test_company_name_common_formats(text, expected_company):
    information = extract_information(clean_message(text))

    assert information["company"] == expected_company


def test_round_number_is_explicit_only():
    info = extract_information(clean_message("Round 1 was communication."))
    assert any(round_info["round_number"] == 1 and round_info["round_type"] == "Communication" for round_info in info["rounds"])

    info = extract_information(clean_message("Round 2 was coding."))
    assert any(round_info["round_number"] == 2 and round_info["round_type"] == "Coding" for round_info in info["rounds"])

    info = extract_information(clean_message("L1 technical interview questions"))
    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] is None for round_info in info["rounds"])

    info = extract_information(clean_message("L2 technical interview questions"))
    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] is None for round_info in info["rounds"])


def test_feedback_is_extracted_separately_from_questions():
    info = extract_information(clean_message("Interview was friendly and mostly resume based. No coding on paper."))

    assert info["questions"] == []
    assert any("friendly" in text.lower() or "resume" in text.lower() or "coding" in text.lower() for text in info["feedback"])


def test_topic_aliases_for_sql_and_string_problems():
    sql_info = extract_information(clean_message("Second highest salary SQL query"))
    assert any(topic in {"SQL", "DBMS"} for topic in sql_info["topics"])

    string_info = extract_information(clean_message("Longest substring without repeating characters"))
    assert any(topic in {"Strings", "Algorithms"} for topic in string_info["topics"])
    assert any("longest substring" in q.lower() for q in string_info["questions"])


def test_company_round_and_difficulty_examples():
    info = extract_information(clean_message("Company: Infosys\nRound: Coding\nQuestions:\nLongest substring without repeating characters\nDifficulty: Hard"))

    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Coding" and round_info["round_number"] is None for round_info in info["rounds"])
    assert "Hard" in info["difficulty"]
    assert any("longest substring" in q.lower() for q in info["questions"])

    info = extract_information(clean_message("Company: Infosys\nRound: Communication\nDifficulty: Easy"))
    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Communication" and round_info["round_number"] is None for round_info in info["rounds"])
    assert "Easy" in info["difficulty"]


def test_company_name_stops_before_round_or_stage_boundary():
    info = extract_information(clean_message("Company: Capgemini\nTechnical interview questions..."))
    assert info["company"] == "Capgemini"

    info = extract_information(clean_message("Company: Infosys\nRound: Technical"))
    assert info["company"] == "Infosys"


def test_role_and_drive_context_extraction_stops_before_cohort_text():
    info = extract_information(
        clean_message(
            "Company: Capgemini\n"
            "Role: hiring for System Engineer in the 2023-27 batch\n"
            "Year: 2026\n"
            "Package: 6.5 LPA"
        )
    )

    assert info["job_role"] == "System Engineer"
    assert info["batch"] == "2023-27"
    assert info["year"] == 2026
    assert info["package"] == "6.5 LPA"


def test_round_technical_field_is_extracted_and_question_boundary_is_respected():
    info = extract_information(clean_message("Company: Infosys\nRound: Technical\nQuestion: What is OOP?\nDifficulty: Medium\nFeedback: Interview was friendly and mostly resume based."))
    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] is None for round_info in info["rounds"])
    assert info["questions"] == ["What is OOP?"]
    assert "Medium" in info["difficulty"]
    assert any("friendly" in item.lower() and "resume" in item.lower() for item in info["feedback"])


def test_feedback_regression_1_company_round_question_difficulty_and_feedback():
    info = extract_information(clean_message(
        "Company: Infosys\nRound: Technical\nQuestion: What is OOP?\nDifficulty: Medium\nFeedback: Interview was friendly and mostly resume based."
    ))
    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Technical" for round_info in info["rounds"])
    assert info["questions"] == ["What is OOP?"]
    assert "Medium" in info["difficulty"]
    assert info["feedback"] == ["Interview was friendly and mostly resume based"]
    assert "OOP" in info["topics"]
    assert "Operating System" not in info["topics"]


def test_feedback_regression_2_os_topic_detection():
    info = extract_information(clean_message("Question: Explain process and thread in Operating System."))
    assert "Operating System" in info["topics"]
    assert "Process" in info["topics"]
    assert "Thread" in info["topics"]


def test_feedback_regression_3_difficulty_and_feedback_boundary():
    info = extract_information(clean_message("Difficulty: Hard\nFeedback: Coding was time consuming."))
    assert info["feedback"] == ["Coding was time consuming"]


def test_feedback_regression_4_feedback_without_prefix():
    info = extract_information(clean_message("Feedback:\nInterview was friendly."))
    assert info["feedback"] == ["Interview was friendly"]


def test_false_operating_system_topic_is_not_inferred_from_oop():
    info = extract_information(clean_message("Question: What is OOP?"))
    assert "OOP" in info["topics"]
    assert "Operating System" not in info["topics"]


def test_extracted_feedback_and_difficulty_are_persisted_with_existing_models():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Infosys")
    session.add(company)
    session.flush()

    drive = PlacementDrive(company_id=company.id, year=2026, job_role="Software Engineer")
    session.add(drive)
    session.flush()

    raw = RawMessage(message_id="1", source="telegram", sender="student", message_text="Company: Infosys\nRound: Technical\nFeedback:\nInterview was friendly and mostly resume based.", placement_drive_id=drive.id)
    session.add(raw)
    session.flush()

    info = extract_information(clean_message(raw.message_text))
    store_extracted_information(session, drive.id, info, raw.id)

    persisted_round = session.query(RecruitmentRound).filter_by(placement_drive_id=drive.id, round_type="Technical").first()
    assert persisted_round is not None
    assert persisted_round.difficulty in {None, "Medium"}

    stored_exp = session.query(Experience).filter_by(placement_drive_id=drive.id).all()
    assert stored_exp
    assert any("friendly" in exp.experience_text.lower() for exp in stored_exp)

    question_count = session.query(Question).filter_by(placement_drive_id=drive.id).count()
    assert question_count >= 0

    session.close()


def test_storage_keeps_explicit_round_context_for_questions():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Infosys")
    session.add(company)
    session.flush()

    drive = PlacementDrive(company_id=company.id, year=2026, job_role="Software Engineer")
    session.add(drive)
    session.flush()

    info = extract_information(clean_message("Company: Infosys\nRound: Technical\nQuestions:\nWhat is OOP?\nWhat is REST API?\nDifficulty: Medium\nFeedback:\nInterview was friendly."))
    store_extracted_information(session, drive.id, info, source_message_id=None)

    technical_round = session.query(RecruitmentRound).filter_by(placement_drive_id=drive.id, round_type="Technical").first()
    assert technical_round is not None
    assert technical_round.difficulty == "Medium"

    questions = session.query(Question).filter_by(placement_drive_id=drive.id).all()
    assert len(questions) >= 2
    assert any("what is oop" in q.question_text.lower() for q in questions)
    for q in questions:
        if "what is oop" in q.question_text.lower():
            assert q.round_id == technical_round.id

    assert session.query(Experience).filter_by(placement_drive_id=drive.id).count() >= 1

    session.close()


def test_storage_does_not_invent_company_when_message_has_no_company():
    info = extract_information(clean_message("Technical round was easy. Asked about OOP and DBMS."))
    assert info["company"] is None
    assert info["difficulty"] == ["Easy"]


def test_same_company_may_share_drive_when_associated():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Infosys")
    session.add(company)
    session.flush()

    drive = PlacementDrive(company_id=company.id, year=2026, job_role="Software Engineer")
    session.add(drive)
    session.flush()

    first = extract_information(clean_message("Company: Infosys\nRound: Technical\nQuestion: What is OOP?"))
    store_extracted_information(session, drive.id, first, source_message_id=None)
    second = extract_information(clean_message("Company: Infosys\nRound: Coding\nQuestion: Reverse a string."))
    store_extracted_information(session, drive.id, second, source_message_id=None)

    rounds = session.query(RecruitmentRound).filter_by(placement_drive_id=drive.id).all()
    questions = session.query(Question).filter_by(placement_drive_id=drive.id).all()
    assert len(rounds) >= 2
    assert len(questions) >= 2

    session.close()


def test_infosys_section_aware_extraction_storage_and_retry_are_idempotent():
    text = (
        "Company: Infosys\n"
        "Role: Associate Software Engineer\n"
        "Eligibility: Minimum 7.5 CGPA and no standing arrears.\n\n"
        "Recruitment flow:\n"
        "Round 1: Aptitude\n"
        "Round 2: Coding\n"
        "Round 3: Managerial Interview\n"
        "Round 4: HR Interview\n\n"
        "Aptitude topics:\n"
        "Logical Reasoning, Quantitative Aptitude, Data Interpretation\n\n"
        "Coding topics:\n"
        "Arrays, Strings, Recursion, Searching\n\n"
        "Technical topics:\n"
        "Java, Python, DBMS, OOP\n\n"
        "Sample questions:\n"
        "1. Find the frequency of each element in an array.\n"
        "2. Write a program to check whether a string is a palindrome.\n"
        "3. Explain method overloading and method overriding.\n"
        "4. What is normalization in DBMS?\n"
        "Difficulty: Medium\n\n"
        "Student feedback:\n"
        "The coding round focused on logical thinking and basic programming concepts."
    )
    info = extract_information(clean_message(text))

    assert [
        (round_info["round_number"], round_info["round_type"])
        for round_info in info["rounds"]
    ] == [
        (1, "Aptitude"),
        (2, "Coding"),
        (3, "Managerial"),
        (4, "HR"),
    ]
    assert len(info["rounds"]) == 4
    expected_topics = {
        "Aptitude": {"Logical Reasoning", "Quantitative Aptitude", "Data Interpretation"},
        "Coding": {"Arrays", "Strings", "Recursion", "Searching"},
        "Technical": {"Java", "Python", "DBMS", "OOP"},
    }
    for category, expected_names in expected_topics.items():
        assert {
            detail["topic"]
            for detail in info["topic_details"]
            if detail["category"] == category
        } == expected_names
    assert set(info["topics"]) == set().union(*expected_topics.values())

    question_details = {
        detail["question"]: detail for detail in info["question_details"]
    }
    coding_questions = [
        question for question in question_details
        if "frequency of each element" in question.lower()
        or "palindrome" in question.lower()
    ]
    technical_questions = [
        question for question in question_details
        if "method overloading" in question.lower()
        or "normalization in dbms" in question.lower()
    ]
    assert len(coding_questions) == 2
    assert len(technical_questions) == 2
    assert all(question_details[q]["category"] == "Coding" for q in coding_questions)
    assert all(question_details[q]["round_number"] == 2 for q in coding_questions)
    assert all(question_details[q]["category"] == "Technical" for q in technical_questions)
    assert all(question_details[q]["round_number"] is None for q in technical_questions)

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Infosys")
    session.add(company)
    session.flush()
    drive = PlacementDrive(
        company_id=company.id,
        job_role="Associate Software Engineer",
        number_of_rounds=4,
    )
    session.add(drive)
    session.flush()
    raw_message = RawMessage(
        message_id="infosys-section-aware",
        source="telegram",
        sender="student",
        message_text=text,
        placement_drive_id=drive.id,
        processed=False,
    )
    session.add(raw_message)
    session.flush()

    store_extracted_information(session, drive.id, info, raw_message.id)
    session.flush()

    persisted_rounds = session.query(RecruitmentRound).filter_by(
        placement_drive_id=drive.id
    ).order_by(RecruitmentRound.round_number).all()
    round_ids = {round_item.round_number: round_item.id for round_item in persisted_rounds}
    assert [(item.round_number, item.round_type) for item in persisted_rounds] == [
        (1, "Aptitude"),
        (2, "Coding"),
        (3, "Managerial"),
        (4, "HR"),
    ]

    topic_associations = (
        session.query(PlacementDriveTopic, Topic)
        .join(Topic, Topic.id == PlacementDriveTopic.topic_id)
        .filter(PlacementDriveTopic.placement_drive_id == drive.id)
        .all()
    )
    associated_topics = {
        (topic.name, association.category): association.round_id
        for association, topic in topic_associations
    }
    for topic_name in expected_topics["Aptitude"]:
        assert associated_topics[(topic_name, "Aptitude")] == round_ids[1]
    for topic_name in expected_topics["Coding"]:
        assert associated_topics[(topic_name, "Coding")] == round_ids[2]
    for topic_name in expected_topics["Technical"]:
        assert associated_topics[(topic_name, "Technical")] is None

    persisted_questions = session.query(Question).filter_by(
        placement_drive_id=drive.id
    ).all()
    by_question_text = {question.question_text: question for question in persisted_questions}
    assert len(persisted_questions) == 4
    for question_text in coding_questions:
        question = by_question_text[question_text]
        assert question.round_id == round_ids[2]
        assert session.query(Topic).filter_by(id=question.topic_id).one().name in {
            "Arrays",
            "Strings",
        }
    for question_text in technical_questions:
        question = by_question_text[question_text]
        assert question.round_id is None
        assert session.query(Topic).filter_by(id=question.topic_id).one().name in {
            "OOP",
            "DBMS",
        }
    assert session.query(EligibilityCriteria).filter_by(
        placement_drive_id=drive.id
    ).count() == 1
    api_result = company_analytics(company.id, session)
    assert len(api_result["rounds"]) == 4
    assert len(api_result["preparation_topics"]) == 11
    assert {
        item["topic"] for item in api_result["topics"]
    } == set().union(*expected_topics.values())
    assert next(
        item["occurrence_count"]
        for item in api_result["topics"]
        if item["topic"] == "Logical Reasoning"
    ) == 0
    assert {
        item["topic"]
        for item in api_result["preparation_topics"]
        if item["category"] == "Technical" and item["round_id"] is None
    } == expected_topics["Technical"]
    api_questions = {
        question["question"]: question
        for question in api_result["frequent_questions"]
    }
    assert all(
        api_questions[q]["round_id"] == round_ids[2]
        for q in coding_questions
    )
    assert all(api_questions[q]["round_id"] is None for q in technical_questions)
    assert all(
        api_questions[q]["topic_category"] == "Coding"
        for q in coding_questions
    )
    assert all(
        api_questions[q]["topic_category"] == "Technical"
        for q in technical_questions
    )
    assert len(frequent_topics(session, drive_id=drive.id)) == 11
    assert len(frequent_questions(session, drive_id=drive.id)) == 4
    initial_topic_link_count = len(topic_associations)
    initial_source_link_count = session.query(QuestionSourceMessage).count()
    initial_round_source_count = session.query(
        RecruitmentRoundSourceMessage
    ).count()
    initial_topic_source_count = session.query(
        PlacementDriveTopicSourceMessage
    ).count()
    initial_eligibility_source_count = session.query(
        EligibilitySourceMessage
    ).count()
    store_extracted_information(session, drive.id, info, raw_message.id)
    session.flush()

    assert session.query(RecruitmentRound).filter_by(
        placement_drive_id=drive.id
    ).count() == 4
    assert session.query(Question).filter_by(placement_drive_id=drive.id).count() == 4
    assert session.query(PlacementDriveTopic).filter_by(
        placement_drive_id=drive.id
    ).count() == initial_topic_link_count == 11
    assert session.query(QuestionSourceMessage).count() == initial_source_link_count == 4
    assert session.query(RecruitmentRoundSourceMessage).count() == initial_round_source_count == 4
    assert session.query(PlacementDriveTopicSourceMessage).count() == initial_topic_source_count == 11
    assert session.query(EligibilitySourceMessage).count() == initial_eligibility_source_count == 1
    persisted_questions = session.query(Question).filter_by(
        placement_drive_id=drive.id
    ).all()
    assert all(question.occurrence_count == 1 for question in persisted_questions)
    assert session.query(EligibilityCriteria).filter_by(
        placement_drive_id=drive.id
    ).count() == 1

    session.close()


def test_storage_does_not_infer_question_round_from_global_topic_category():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Unassigned Topic Co")
    session.add(company)
    session.flush()
    drive = PlacementDrive(company_id=company.id)
    session.add(drive)
    session.flush()
    question_text = "Describe a useful operation on an array."
    information = {
        "rounds": [
            {
                "round_number": 1,
                "round_type": "Coding",
                "description": "Coding",
            }
        ],
        "topics": ["Arrays"],
        "topic_details": [],
        "questions": [question_text],
        "question_details": [
            {
                "question": question_text,
                "topic": None,
                "category": None,
                "round_number": None,
            }
        ],
    }

    store_extracted_information(session, drive.id, information)
    session.flush()

    question = session.query(Question).filter_by(
        placement_drive_id=drive.id
    ).one()
    topic_association = session.query(PlacementDriveTopic).filter_by(
        placement_drive_id=drive.id
    ).one()
    assert question.round_id is None
    assert topic_association.round_id is None

    session.close()


def test_company_analytics_selects_and_isolates_a_placement_drive():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Drive Selection Co")
    other_company = Company(name="Different Company")
    session.add_all([company, other_company])
    session.flush()
    associate_drive = PlacementDrive(
        company_id=company.id,
        job_role="Associate Engineer",
        number_of_rounds=1,
    )
    systems_drive = PlacementDrive(
        company_id=company.id,
        job_role="Systems Engineer",
        number_of_rounds=1,
    )
    foreign_drive = PlacementDrive(
        company_id=other_company.id,
        job_role="Associate Engineer",
    )
    session.add_all([associate_drive, systems_drive, foreign_drive])
    session.flush()

    associate_round = RecruitmentRound(
        placement_drive_id=associate_drive.id,
        round_number=1,
        round_type="Coding",
    )
    systems_round = RecruitmentRound(
        placement_drive_id=systems_drive.id,
        round_number=1,
        round_type="Technical",
    )
    session.add_all([associate_round, systems_round])
    session.flush()

    associate_question = Question(
        placement_drive_id=associate_drive.id,
        round_id=associate_round.id,
        question_text="Reverse an array.",
    )
    systems_question = Question(
        placement_drive_id=systems_drive.id,
        round_id=systems_round.id,
        question_text="Explain operating system scheduling.",
    )
    session.add_all([associate_question, systems_question])
    session.commit()

    default_result = company_analytics(company.id, session)
    selected_result = company_analytics(
        company.id,
        session,
        drive_id=associate_drive.id,
    )

    assert default_result["drive_id"] == systems_drive.id
    assert default_result["job_role"] == "Systems Engineer"
    assert {
        question["question"]
        for question in default_result["frequent_questions"]
    } == {"Explain operating system scheduling."}
    assert selected_result["drive_id"] == associate_drive.id
    assert selected_result["job_role"] == "Associate Engineer"
    assert {
        question["question"]
        for question in selected_result["frequent_questions"]
    } == {"Reverse an array."}
    assert [drive["id"] for drive in selected_result["available_drives"]] == [
        systems_drive.id,
        associate_drive.id,
    ]

    with pytest.raises(HTTPException) as error:
        company_analytics(company.id, session, drive_id=foreign_drive.id)
    assert error.value.status_code == 404

    session.close()


def test_reprocess_preview_is_read_only_and_checks_role_match():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Preview Co")
    session.add(company)
    session.flush()
    drive = PlacementDrive(
        company_id=company.id,
        job_role="Associate Engineer",
    )
    raw = RawMessage(
        message_id="preview-only",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Preview Co\n"
            "Role: Associate Engineer\n"
            "Round 1: Coding\n"
            "Question: Reverse an array."
        ),
        placement_drive_id=None,
        processed=True,
    )
    session.add_all([drive, raw])
    session.commit()

    before_company_count = session.query(Company).count()
    before_drive_count = session.query(PlacementDrive).count()
    before_round_count = session.query(RecruitmentRound).count()
    before_question_count = session.query(Question).count()
    preview = inspect_message(session, raw)

    assert preview["candidate_drive_id"] == drive.id
    assert preview["would_create_drive"] is False
    assert preview["validation_error"] is None
    assert preview["extracted_rounds"] == 1
    assert preview["extracted_questions"] == 1
    assert preview["proposed"]["rounds"][0]["round_type"] == "Coding"
    assert preview["proposed"]["questions"][0]["round_number"] == 1
    assert preview["current"] == {
        "rounds": [],
        "topics": [],
        "questions": [],
    }
    assert session.query(Company).count() == before_company_count
    assert session.query(PlacementDrive).count() == before_drive_count
    assert session.query(RecruitmentRound).count() == before_round_count
    assert session.query(Question).count() == before_question_count
    assert raw.processed is True
    assert raw.placement_drive_id is None

    raw.placement_drive_id = drive.id
    raw.message_text = raw.message_text.replace(
        "Associate Engineer", "Systems Engineer"
    )
    mismatch_preview = inspect_message(session, raw)
    assert "match linked drive role" in mismatch_preview["validation_error"]
    assert mismatch_preview["before"]["rounds"] == 0
    assert session.query(PlacementDrive).count() == before_drive_count

    session.close()


def test_job_role_matching_reuses_same_role_and_separates_different_roles():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    first_text = (
        "Infosys placement update: Recruitment date 30 September 2026. "
        "Role: Associate Software Engineer. Eligibility: 7 CGPA."
    )
    same_role_text = (
        "Infosys placement update: Role: Associate Software Engineer. "
        "Questions: Explain OOP."
    )
    different_role_text = (
        "Infosys placement update: Role: Systems Engineer. "
        "Eligibility: no standing arrears."
    )
    role_unknown_text = "Company: Infosys\nInterview feedback was shared."
    assert infer_job_role_from_message(first_text) == "Associate Software Engineer"
    assert infer_job_role_from_message(different_role_text) == "Systems Engineer"

    first_drive = get_or_create_placement_drive_for_message(
        session, "Infosys", first_text
    )
    store_extracted_information(
        session,
        first_drive.id,
        extract_information(clean_message(first_text)),
    )
    reused_drive = get_or_create_placement_drive_for_message(
        session, "Infosys", same_role_text
    )
    other_drive = get_or_create_placement_drive_for_message(
        session, "Infosys", different_role_text
    )
    with pytest.raises(DriveMatchAmbiguous):
        get_or_create_placement_drive_for_message(
            session, "Infosys", role_unknown_text
        )

    assert reused_drive.id == first_drive.id
    assert other_drive.id != first_drive.id
    assert session.query(PlacementDrive).filter_by(
        company_id=first_drive.company_id
    ).count() == 2
    session.close()


def test_drive_matching_uses_batch_and_rejects_ambiguous_role_matches():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Cohort Matching Co")
    session.add(company)
    session.flush()
    first_drive = PlacementDrive(
        company_id=company.id,
        job_role="Software Engineer",
        batch="2023-27",
    )
    second_drive = PlacementDrive(
        company_id=company.id,
        job_role="Software Engineer",
        batch="2024-28",
    )
    session.add_all([first_drive, second_drive])
    session.commit()

    matched = get_or_create_placement_drive_for_message(
        session,
        "Cohort Matching Co",
        "Company: Cohort Matching Co\n"
        "Role: Software Engineer\n"
        "Batch: 2023-27",
    )
    assert matched.id == first_drive.id

    with pytest.raises(DriveMatchAmbiguous):
        get_or_create_placement_drive_for_message(
            session,
            "Cohort Matching Co",
            "Company: Cohort Matching Co\nRole: Software Engineer",
        )
    assert session.query(PlacementDrive).filter_by(company_id=company.id).count() == 2
    session.close()


def test_same_question_text_is_not_merged_across_preparation_contexts():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Question Context Co")
    session.add(company)
    session.flush()
    drive = PlacementDrive(company_id=company.id, job_role="Engineer")
    session.add(drive)
    session.flush()

    coding_message = RawMessage(
        message_id="context-coding",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Question Context Co\n"
            "Role: Engineer\n"
            "Round 1: Coding\n"
            "Coding topics: Arrays\n"
            "Question: Find the frequency of each element in an array."
        ),
    )
    technical_message = RawMessage(
        message_id="context-technical",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Question Context Co\n"
            "Role: Engineer\n"
            "Round 1: Technical\n"
            "Technical topics: Arrays\n"
            "Question: Find the frequency of each element in an array."
        ),
    )
    session.add_all([coding_message, technical_message])
    session.flush()

    store_extracted_information(
        session,
        drive.id,
        extract_information(clean_message(coding_message.message_text)),
        coding_message.id,
    )
    store_extracted_information(
        session,
        drive.id,
        extract_information(clean_message(technical_message.message_text)),
        technical_message.id,
    )
    session.flush()

    questions = session.query(Question).filter_by(
        placement_drive_id=drive.id
    ).all()
    assert len(questions) == 2
    assert {
        question.preparation_category for question in questions
    } == {"Coding", "Technical"}
    assert len(
        {
            (
                question.round_id,
                question.topic_id,
                question.preparation_category,
            )
            for question in questions
        }
    ) == 2
    assert session.query(QuestionSourceMessage).count() == 2
    assert all(question.occurrence_count == 1 for question in questions)
    session.close()


def test_technical_topic_section_stays_standalone_without_explicit_round_link():
    text = (
        "Company: Infosys\n"
        "Round 1: Aptitude\n"
        "Round 2: Technical Interview\n"
        "Technical topics:\n"
        "Java, DBMS\n"
        "Sample questions:\n"
        "Explain normalization in DBMS.\n"
    )
    info = extract_information(clean_message(text))
    assert len(info["rounds"]) == 2
    assert all(
        detail["round_number"] is None
        for detail in info["topic_details"]
        if detail["category"] == "Technical"
    )
    assert info["question_details"][0]["round_number"] is None

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    company = Company(name="Infosys")
    session.add(company)
    session.flush()
    drive = PlacementDrive(company_id=company.id)
    session.add(drive)
    session.flush()

    store_extracted_information(session, drive.id, info)

    technical_topics = (
        session.query(PlacementDriveTopic, Topic)
        .join(Topic, Topic.id == PlacementDriveTopic.topic_id)
        .filter(
            PlacementDriveTopic.placement_drive_id == drive.id,
            PlacementDriveTopic.category == "Technical",
        )
        .all()
    )
    assert {topic.name for _, topic in technical_topics} == {"Java", "DBMS"}
    assert all(association.round_id is None for association, _ in technical_topics)
    question = session.query(Question).filter(
        Question.placement_drive_id == drive.id
    ).one()
    assert question.round_id is None
    session.close()


def test_process_raw_message_handles_natural_mistral_message_without_existing_drive():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    raw = RawMessage(
        message_id="231",
        source="telegram",
        sender="Meena",
        message_text=(
            "Name: Meena\n"
            "Company: mistral\n"
            "Feedback: Interview was very friendly, only resume based. No coding on paper.\n"
            "Questions:\n"
            "Self intro\n"
            "Explain final year project\n"
            "What is OOPS?\n"
            "Difference between abstract class and interface?\n"
            "Write a query for highest salary in SQL.\n"
            "Code: Longest substring without repeating characters\n"
            "What is OOPs\n"
            "Explain microservices vs monolithic\n"
            "What is crud\n"
            "Explain your GitHub projects."
        ),
        message_date=None,
        placement_drive_id=None,
        processed=False,
    )
    session.add(raw)
    session.flush()

    response = process_raw_message(raw.id, db=session)

    assert response["processed"] is True
    assert response["placement_drive_id"] is not None
    assert session.query(Company).filter(func.lower(Company.name) == "mistral").count() == 1
    assert session.query(PlacementDrive).filter_by(id=response["placement_drive_id"]).count() == 1
    assert session.query(Question).filter_by(placement_drive_id=response["placement_drive_id"]).count() > 0
    assert session.query(Experience).filter_by(placement_drive_id=response["placement_drive_id"]).count() > 0

    repeated = process_raw_message(raw.id, db=session)
    assert repeated["processed"] is True
    assert session.query(Company).filter(func.lower(Company.name) == "mistral").count() == 1
    assert session.query(PlacementDrive).filter_by(company_id=response["placement_drive_id"]).count() == 1

    session.close()


def test_extract_information_for_mistral_telegram_question_list():
    text = (
        "Name : Meena\n"
        "Dept : CSE\n"
        "Company: mistral\n\n"
        "Feedback:\n"
        "Interview was very friendly, only resume based. No coding on paper.\n\n"
        "L1,L2 questions:\n"
        "Self intro,\n"
        "Explain final year project,\n"
        "What is OOPS?\n"
        "Difference between abstract class and interface?\n"
        "Write a query for highest salary in SQL.\n"
        "Code: Longest substring without repeating characters\n"
        "What is OOPs\n"
        "Explain microservices vs monolithic,\n"
        "What is crud\n"
        "Explain your GitHub projects."
    )

    info = extract_information(clean_message(text))

    assert info["company"] == "Mistral"
    assert info["difficulty"] == []
    assert any("interview was very friendly" in item.lower() and "resume based" in item.lower() and "no coding on paper" in item.lower() for item in info["feedback"])
    assert not any("l1" in item.lower() or "l2" in item.lower() for item in info["feedback"])
    assert any("self intro" in item.lower() for item in info["questions"])
    assert any("final year project" in item.lower() for item in info["questions"])
    assert any("what is oops" in item.lower() for item in info["questions"])
    assert any("difference between abstract class and interface" in item.lower() for item in info["questions"])
    assert any("highest salary" in item.lower() and "sql" in item.lower() for item in info["questions"])
    assert any("longest substring" in item.lower() for item in info["questions"])
    assert any("microservices" in item.lower() and "monolithic" in item.lower() for item in info["questions"])
    assert any("what is crud" in item.lower() for item in info["questions"])
    assert any("github projects" in item.lower() for item in info["questions"])
    assert len(info["questions"]) >= 9
    assert info["rounds"] == []


def test_natural_telegram_question_parsing_regressions():
    accenture = (
        "Self intro\n"
        "Explain final year project\n"
        "What is OOPS?\n"
        "what is polymorphism\n"
        "what is method overloading?\n"
        "what is method overiding?\n"
        "why is java platform independent?\n"
        "explain cloud resources Explain microservices vs monolithic?\n"
        "What is crud\n"
        "Explain your GitHub projects"
    )
    econ = (
        "What is a circuit?What is the? difference between AC and DC current?What does Ohm's Law state?\n"
        "What is the purpose of a resistor in a circuit?\n"
        "What is a capacitor, and what does it store?\n"
        "What is the difference between a conductor and an insulator?\n"
        "What is a diode, and which way does it let current flow?\n"
        "What is a transistor, and what are its two main functions?\n"
        "What is hallunication in ai?\n"
        "What is a diode, and which way does it let current flow?\n"
        "What is a transistor, and what are its two main functions?"
    )
    cognizant = (
        "Explain Cloud Computing\n"
        "What is SaaS, PaaS, IaaS?\n"
        "What did you do in your cloud project?\n"
        "What is polymorphism?\n"
        "Method overloading vs overriding?\n"
        "Explain your ML model accuracy\n"
        "what is AI agent?\n"
        "what is the difference between springboot and maven?\n"
        "What is overfitting vs underfitting?\n"
        "What is confusion matrix?\n"
        "SQL JOINS with examples.\n"
        "Puzzle: You have 8 balls, 1 is heavy, find in min weighings."
    )
    deloitte = (
        "Explain List vs Tuple vs Set\n"
        "why java?\n"
        "features of java?\n"
        "What is Python interpreted language?\n"
        "What is exception handling in java?\n"
        "Write code for prime numbers 1-N.\n"
        "What is SDLC?\n"
        "What is 1NF, 2NF, 3NF?\n"
        "Check anagram of two strings.\n"
        "Find duplicate in array.\n"
        "Explain your internship."
    )
    mistral = (
        "Self intro\n"
        "Explain final year project\n"
        "What is OOPS?\n"
        "Difference between abstract class and interface?\n"
        "Write a query for highest salary in SQL.\n"
        "Longest substring without repeating characters\n"
        "What is OOPs\n"
        "Explain microservices vs monolithic\n"
        "What is crud\n"
        "Explain your GitHub projects"
    )

    accenture_info = extract_information(clean_message(accenture))
    assert any("explain cloud resources" in q.lower() for q in accenture_info["questions"])
    assert any("microservices vs monolithic" in q.lower() for q in accenture_info["questions"])
    assert not any(q.lower() in {"explain?", "what?", "write?", "s?", "l1?"} for q in accenture_info["questions"])
    assert any("what did you do in your cloud project" in q.lower() for q in extract_information(clean_message(cognizant))["questions"])

    econ_info = extract_information(clean_message(econ))
    assert any("what is a circuit" in q.lower() for q in econ_info["questions"])
    assert any("difference between ac and dc current" in q.lower() for q in econ_info["questions"])
    assert any("what does ohm's law state" in q.lower() for q in econ_info["questions"])
    bad_artifact_patterns = re.compile(r"^(?:s|l1|l2|what|explain|write)\??$", re.IGNORECASE)
    assert all(not bad_artifact_patterns.fullmatch(q.strip()) for q in econ_info["questions"])

    cognizant_info = extract_information(clean_message(cognizant))
    assert any("explain cloud computing" in q.lower() for q in cognizant_info["questions"])
    assert any("what is saas, paas, iaas" in q.lower() for q in cognizant_info["questions"])
    assert any("what did you do in your cloud project" in q.lower() for q in cognizant_info["questions"])
    assert any("springboot" in q.lower() and "maven" in q.lower() and "difference" in q.lower() for q in cognizant_info["questions"])
    assert any(
        ("8 balls" in q.lower() and "heavy" in q.lower()) or "find in min weighings" in q.lower()
        for q in cognizant_info["questions"]
    )
    bad_artifact_patterns = re.compile(r"^(?:s|l1|l2|what|explain|write)\??$", re.IGNORECASE)
    assert all(not bad_artifact_patterns.fullmatch(q.strip()) for q in cognizant_info["questions"])

    deloitte_info = extract_information(clean_message(deloitte))
    assert any("list vs tuple vs set" in q.lower() for q in deloitte_info["questions"])
    assert any("write code for prime numbers 1-n" in q.lower() for q in deloitte_info["questions"])
    assert any("check anagram of two strings" in q.lower() for q in deloitte_info["questions"])
    assert any("find duplicate in array" in q.lower() for q in deloitte_info["questions"])
    bad_artifact_patterns = re.compile(r"^(?:s|l1|l2|what|why|explain|write)\??$", re.IGNORECASE)
    assert all(not bad_artifact_patterns.fullmatch(q.strip()) for q in deloitte_info["questions"])

    mistral_info = extract_information(clean_message(mistral))
    assert any("self intro" in q.lower() for q in mistral_info["questions"])
    assert any("final year project" in q.lower() for q in mistral_info["questions"])
    assert any("what is oops" in q.lower() for q in mistral_info["questions"])
    assert any("difference between abstract class and interface" in q.lower() for q in mistral_info["questions"])
    assert any("highest salary" in q.lower() and "sql" in q.lower() for q in mistral_info["questions"])
    assert any("longest substring" in q.lower() for q in mistral_info["questions"])
    assert any("microservices vs monolithic" in q.lower() for q in mistral_info["questions"])
    assert any("what is crud" in q.lower() for q in mistral_info["questions"])
    assert any("github projects" in q.lower() for q in mistral_info["questions"])
    assert len(mistral_info["questions"]) >= 9


def test_process_raw_message_reuses_existing_matching_drive_when_metadata_is_explicit():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Infosys")
    session.add(company)
    session.flush()

    drive = PlacementDrive(company_id=company.id, year=2026, job_role="Software Engineer")
    session.add(drive)
    session.flush()

    raw = RawMessage(
        message_id="999",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Infosys\n"
            "Role: Software Engineer\n"
            "Round 1: Aptitude\n"
            "Feedback: Interview was very friendly and mostly resume based."
        ),
        placement_drive_id=None,
        processed=False,
    )
    session.add(raw)
    session.flush()

    response = process_raw_message(raw.id, db=session)

    assert response["placement_drive_id"] == drive.id
    assert raw.placement_drive_id == drive.id
    assert session.query(Question).filter_by(placement_drive_id=drive.id).count() >= 0

    session.close()


def test_process_raw_message_does_not_process_when_company_is_missing(caplog):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    raw = RawMessage(
        message_id="missing-company",
        source="telegram",
        sender="student",
        message_text="Interview experience was useful.",
        processed=False,
    )
    session.add(raw)
    session.commit()
    original_text = raw.message_text

    with pytest.raises(HTTPException) as error:
        process_raw_message(raw.id, db=session)

    session.refresh(raw)
    assert error.value.status_code == 422
    assert error.value.detail["status"] == "failed"
    assert error.value.detail["processed"] is False
    assert raw.processed is False
    assert raw.placement_drive_id is None
    assert raw.message_text == original_text
    assert session.query(Company).count() == 0
    assert session.query(PlacementDrive).count() == 0
    assert "Company not detected" in caplog.text

    session.close()


def test_process_raw_message_stays_unprocessed_when_drive_match_is_ambiguous():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    company = Company(name="Ambiguous Match Co")
    session.add(company)
    session.flush()
    session.add_all(
        [
            PlacementDrive(
                company_id=company.id,
                job_role="Software Engineer",
                batch="2023-27",
            ),
            PlacementDrive(
                company_id=company.id,
                job_role="Software Engineer",
                batch="2024-28",
            ),
        ]
    )
    raw = RawMessage(
        message_id="ambiguous-drive",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Ambiguous Match Co\n"
            "Role: Software Engineer\n"
            "Question: Explain object-oriented programming."
        ),
        processed=False,
    )
    session.add(raw)
    session.commit()
    original_text = raw.message_text

    with pytest.raises(HTTPException) as error:
        process_raw_message(raw.id, db=session)

    session.refresh(raw)
    assert error.value.status_code == 409
    assert error.value.detail["status"] == "ambiguous"
    assert raw.processed is False
    assert raw.placement_drive_id is None
    assert raw.message_text == original_text
    assert session.query(PlacementDrive).filter_by(company_id=company.id).count() == 2
    assert session.query(Question).count() == 0
    session.close()


def test_process_raw_message_rolls_back_linking_when_storage_fails(monkeypatch, caplog):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    raw = RawMessage(
        message_id="storage-failure",
        source="telegram",
        sender="student",
        message_text="Company: Zentropy\nRole: Software Engineer\nInterview was useful.",
        processed=False,
    )
    session.add(raw)
    session.commit()
    original_text = raw.message_text

    def fail_storage(**kwargs):
        assert kwargs["placement_drive_id"]
        assert kwargs["information"]["company"] == "Zentropy"
        raise RuntimeError("simulated storage failure")

    monkeypatch.setattr(
        "nlp.raw_message_processor.store_extracted_information",
        fail_storage,
    )

    with pytest.raises(HTTPException) as error:
        process_raw_message(raw.id, db=session)

    session.refresh(raw)
    assert error.value.status_code == 500
    assert error.value.detail["status"] == "failed"
    assert error.value.detail["processed"] is False
    assert raw.processed is False
    assert raw.placement_drive_id is None
    assert raw.message_text == original_text
    assert session.query(Company).count() == 0
    assert session.query(PlacementDrive).count() == 0
    assert "simulated storage failure" in caplog.text

    session.close()


def test_process_raw_message_retry_reuses_company_and_placement_drive():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    raw = RawMessage(
        message_id="retry-message",
        source="telegram",
        sender="student",
        message_text="Company: LTIMindtree\nRole: Software Engineer\nInterview was useful.",
        processed=False,
    )
    session.add(raw)
    session.commit()
    original_text = raw.message_text

    first_response = process_raw_message(raw.id, db=session)
    second_response = process_raw_message(raw.id, db=session)

    assert first_response["placement_drive_id"] == second_response["placement_drive_id"]
    assert session.query(Company).filter_by(name="LTIMindtree").count() == 1
    assert session.query(PlacementDrive).count() == 1
    assert raw.processed is True
    assert second_response["already_processed"] is True
    assert raw.message_text == original_text

    session.close()


def test_processed_message_retry_preserves_question_contributors_and_counts():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    messages = [
        RawMessage(
            message_id=f"contributor-{index}",
            source="telegram",
            sender="student",
            message_text=(
                "Company: Infosys\n"
                "Round: Technical\n"
                "Question: What is OOP?\n"
                "Eligibility: 7 CGPA with no active backlogs."
            ),
            processed=False,
        )
        for index in (1, 2)
    ]
    session.add_all(messages)
    session.commit()

    first_response = process_raw_message(messages[0].id, db=session)
    second_response = process_raw_message(messages[1].id, db=session)

    question = session.query(Question).filter_by(
        placement_drive_id=first_response["placement_drive_id"],
        question_text="What is OOP?",
    ).one()
    assert first_response["placement_drive_id"] == second_response["placement_drive_id"]
    assert question.occurrence_count == 2
    assert question.source_message_id == messages[0].id
    assert {
        source.raw_message_id
        for source in session.query(QuestionSourceMessage)
        .filter_by(question_id=question.id)
        .all()
    } == {messages[0].id, messages[1].id}
    assert session.query(EligibilityCriteria).filter_by(
        placement_drive_id=first_response["placement_drive_id"]
    ).count() == 1

    retry_response = process_raw_message(messages[1].id, db=session)
    session.refresh(question)

    assert retry_response["already_processed"] is True
    assert question.occurrence_count == 2
    assert session.query(QuestionSourceMessage).filter_by(
        question_id=question.id
    ).count() == 2
    assert session.query(EligibilityCriteria).filter_by(
        placement_drive_id=first_response["placement_drive_id"]
    ).count() == 1

    session.close()


def test_explicit_reprocessing_updates_in_place_without_inflating_counts():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    original_text = (
        "Company: Infosys\n"
        "Role: Associate Engineer\n"
        "Round 1: Coding\n"
        "Coding topics: Arrays\n"
        "Question: Find the frequency of each element in an array.\n"
        "Eligibility: 7 CGPA with no active backlogs."
    )
    raw = RawMessage(
        message_id="safe-explicit-reprocess",
        source="telegram",
        sender="student",
        message_text=original_text,
        processed=False,
    )
    session.add(raw)
    session.commit()

    first = process_raw_message(raw.id, db=session)
    retry = process_raw_message(raw.id, reprocess=True, db=session)

    drive_id = first["placement_drive_id"]
    question = session.query(Question).filter_by(
        placement_drive_id=drive_id
    ).one()
    assert retry["processed"] is True
    assert retry["placement_drive_id"] == drive_id
    assert raw.message_text == original_text
    assert raw.processed is True
    assert session.query(RecruitmentRound).filter_by(
        placement_drive_id=drive_id
    ).count() == 1
    assert question.occurrence_count == 1
    assert session.query(QuestionSourceMessage).filter_by(
        question_id=question.id,
        raw_message_id=raw.id,
    ).count() == 1
    assert session.query(EligibilityCriteria).filter_by(
        placement_drive_id=drive_id
    ).count() == 1

    session.close()


def test_failed_message_processing_can_retry_without_partial_records(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    raw = RawMessage(
        message_id="retry-after-failure",
        source="telegram",
        sender="student",
        message_text=(
            "Company: Zentropy\n"
            "Round: Technical\n"
            "Question: What is OOP?\n"
            "Eligibility: 7 CGPA with no active backlogs."
        ),
        processed=False,
    )
    session.add(raw)
    session.commit()

    from nlp import raw_message_processor

    real_store = raw_message_processor.store_extracted_information
    failed_once = False

    def fail_first_store(**kwargs):
        nonlocal failed_once
        result = real_store(**kwargs)
        if not failed_once:
            failed_once = True
            raise RuntimeError("simulated temporary failure")
        return result

    monkeypatch.setattr(
        raw_message_processor,
        "store_extracted_information",
        fail_first_store,
    )

    with pytest.raises(HTTPException) as error:
        process_raw_message(raw.id, db=session)

    session.refresh(raw)
    assert error.value.status_code == 500
    assert raw.processed is False
    assert raw.placement_drive_id is None
    assert session.query(Company).count() == 0
    assert session.query(PlacementDrive).count() == 0
    assert session.query(Question).count() == 0
    assert session.query(QuestionSourceMessage).count() == 0
    assert session.query(EligibilityCriteria).count() == 0

    response = process_raw_message(raw.id, db=session)
    assert response["processed"] is True
    assert raw.processed is True
    assert session.query(Question).count() == 1
    assert session.query(QuestionSourceMessage).count() == 1
    assert session.query(EligibilityCriteria).count() == 1

    session.close()