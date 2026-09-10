import pytest

from nlp.cleaner import clean_message
from nlp.classifier import classify_message
from nlp.extractor import extract_information


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