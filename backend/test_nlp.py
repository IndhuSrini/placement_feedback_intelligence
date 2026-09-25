import re

import pytest
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Company, Experience, PlacementDrive, Question, RawMessage, RecruitmentRound
from nlp.cleaner import clean_message
from nlp.classifier import classify_message
from nlp.extractor import extract_information
from nlp.storage import store_extracted_information
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


def test_company_and_round_rule_regressions():
    info = extract_information(clean_message("Company: Infosys\nRound: Technical\nWhat is OOP?\nDifference between abstract class and interface?\nDifficulty: Medium\nInterview was friendly and mostly resume based."))

    assert info["company"] == "Infosys"
    assert any(round_info["round_type"] == "Technical" and round_info["round_number"] is None for round_info in info["rounds"])
    assert "Medium" in info["difficulty"]
    assert any("friendly" in text.lower() or "resume" in text.lower() for text in info["feedback"])
    assert any("what is oop" in q.lower() for q in info["questions"])
    assert any("abstract class" in q.lower() for q in info["questions"])


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