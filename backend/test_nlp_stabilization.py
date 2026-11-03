import pytest

from nlp.cleaner import clean_message
from nlp.classifier import classify_message
from nlp.extractor import (
    extract_information,
    extract_questions,
    extract_rounds,
    extract_topics,
    normalize_question_text,
)
from nlp.duplicate_detector import calculate_similarity, is_duplicate


# ==============================================================================
# 1. TECH MAHINDRA MULTI-ROUND TEST (The exact canonical prompt example)
# ==============================================================================

TECH_MAHINDRA_MESSAGE = """Company: Tech Mahindra

Role: Software Engineer

Recruitment Process:

Round 1 – Communication Assessment
Topics:
- Reading Comprehension
- Grammar
- Vocabulary

Round 2 – Quantitative and Logical Aptitude
Topics:
- Percentages
- Ratios
- Profit and Loss
- Logical Reasoning

Round 3 – Coding Assessment
Questions:
- Find overlapping intervals.
- Swap two numbers without using a temporary variable.
- Print the Fibonacci series.

Round 4 – HR Interview
Questions:
- Are you willing to relocate?
- What are your hobbies?

Difficulty: Medium"""


def test_tech_mahindra_multiround_extraction():
    info = extract_information(clean_message(TECH_MAHINDRA_MESSAGE))

    # Company & Role
    assert info["company"] == "Tech Mahindra"
    assert info["job_role"] == "Software Engineer"
    assert info["difficulty"] == ["Medium"]

    # All 4 rounds must be extracted with numbers and correct types
    rounds = info["rounds"]
    assert len(rounds) == 4, f"Expected 4 rounds, got {len(rounds)}: {rounds}"

    round_map = {r["round_number"]: r["round_type"] for r in rounds}
    assert round_map.get(1) == "Communication"
    assert round_map.get(2) == "Aptitude"
    assert round_map.get(3) == "Coding"
    assert round_map.get(4) == "HR"

    # Topics must be mapped to their source round and categories
    topics = info["topics"]
    assert "Reading Comprehension" in topics
    assert "Grammar" in topics
    assert "Vocabulary" in topics
    assert "Percentages" in topics
    assert any("ratio" in t.lower() for t in topics)
    assert "Profit and Loss" in topics
    assert "Logical Reasoning" in topics

    # "Process" must NOT be extracted as a topic from "Recruitment Process:"
    assert "Process" not in topics

    # Check topic details have correct round numbers and categories
    topic_details = info["topic_details"]
    comm_topics = [d for d in topic_details if d.get("round_number") == 1]
    assert len(comm_topics) >= 3
    for d in comm_topics:
        assert d["category"] in {"Communication", "Verbal Ability"}

    apt_topics = [d for d in topic_details if d.get("round_number") == 2]
    assert len(apt_topics) >= 3
    for d in apt_topics:
        assert d["category"] in {"Aptitude", "Quantitative Aptitude", "Logical Reasoning"}

    # Questions must be extracted with question starters like Find, Swap, Print
    questions = info["questions"]
    assert any("overlapping intervals" in q.lower() for q in questions)
    assert any("swap two numbers" in q.lower() for q in questions)
    assert any("fibonacci" in q.lower() for q in questions)
    assert any("relocate" in q.lower() for q in questions)
    assert any("hobbies" in q.lower() for q in questions)

    # Check question details: category and round linkage
    q_details = info["question_details"]
    coding_qs = [d for d in q_details if "overlapping" in d["question"].lower() or "swap" in d["question"].lower() or "fibonacci" in d["question"].lower()]
    assert len(coding_qs) == 3
    for qd in coding_qs:
        assert qd["round_number"] == 3
        assert qd["category"] == "Coding"

    hr_qs = [d for d in q_details if "relocate" in d["question"].lower() or "hobbies" in d["question"].lower()]
    assert len(hr_qs) == 2
    for qd in hr_qs:
        assert qd["round_number"] == 4
        assert qd["category"] == "HR"


# ==============================================================================
# 2. HEXAWARE MULTI-ROUND TEST (Realistic Placement Message)
# ==============================================================================

HEXAWARE_MESSAGE = """Hexaware Placement Drive - 2026

Company: Hexaware
Role: Graduate Engineer Trainee
Recruitment Date: 28 September 2026

Eligibility Criteria:
- Minimum 7 CGPA
- No active backlogs
- CSE, IT and related branches
- Batch: 2023-2027

Recruitment Process:

Round 1 – Group Discussion (GD)
Candidates participated in a Group Discussion. Communication skills, confidence, teamwork and ability to express ideas were evaluated.

Round 2 – Aptitude, Technical and Programming Assessment
The assessment included quantitative aptitude, logical reasoning, technical questions and programming problems.

Programming questions included:
- Sort a string in alphabetical order.
- Find duplicate characters in a string.
- Reverse a string without using a built-in reverse function.
- Find the first non-repeating character in a string.
- Check whether a string is a palindrome.

Technical topics included:
- Java
- OOP
- Polymorphism
- Inheritance
- Encapsulation
- Abstraction
- JDK, JRE and JVM
- Exception handling
- Strings
- Arrays
- Collections

Round 3 – Technical Interview
The technical interview focused mainly on Java and object-oriented programming.

Questions asked:

1. What is Java and why is it platform independent?
2. What is the difference between JDK, JRE and JVM?
3. What is polymorphism? Explain compile-time and runtime polymorphism.
4. What is method overloading and method overriding?
5. What are the four pillars of OOP?
6. Explain inheritance in Java with an example.
7. What is encapsulation?
8. What is abstraction and how is it achieved in Java?
9. What is the difference between an abstract class and an interface?
10. Why are Strings immutable in Java?
11. What is the difference between String, StringBuilder and StringBuffer?
12. What is exception handling in Java?
13. What is the difference between checked and unchecked exceptions?
14. What is the difference between ArrayList and LinkedList?
15. What is the difference between == and equals() in Java?
16. What is the difference between a class and an object?

Round 4 – HR Interview
HR questions included:
- Tell me about yourself.
- What are your strengths and weaknesses?
- Why do you want to join Hexaware?
- Why should we hire you?
- Are you willing to relocate?
- Where do you see yourself in five years?

Overall Difficulty: Medium
Technical Interview Difficulty: Medium
Programming Difficulty: Medium"""


def test_hexaware_multiround_extraction():
    info = extract_information(clean_message(HEXAWARE_MESSAGE))

    assert info["company"] == "Hexaware"
    assert info["job_role"] == "Graduate Engineer Trainee"
    assert info["minimum_cgpa"] == 7.0
    assert info["maximum_backlogs"] == 0

    # 4 distinct rounds
    rounds = info["rounds"]
    assert len(rounds) == 4, f"Expected 4 rounds, got {len(rounds)}: {rounds}"

    # Verify programming questions under Round 2 are extracted
    questions = info["questions"]
    assert any("sort a string" in q.lower() for q in questions)
    assert any("duplicate characters" in q.lower() for q in questions)
    assert any("palindrome" in q.lower() for q in questions)

    # Verify compound questions are NOT split into fragments
    assert any("what is java and why is it platform independent" in q.lower() for q in questions)
    assert not any(q.lower().strip() == "why is it platform independent?" for q in questions)

    assert any("what is abstraction and how is it achieved in java" in q.lower() for q in questions)
    assert not any(q.lower().strip() == "how is it achieved in java?" for q in questions)

    # Verify HR questions are extracted and belong to Round 4 / Category HR
    q_details = info["question_details"]
    hire_q = next((d for d in q_details if "why should we hire you" in d["question"].lower()), None)
    assert hire_q is not None
    assert hire_q["round_number"] == 4
    assert hire_q["category"] == "HR"

    relocate_q = next((d for d in q_details if "willing to relocate" in d["question"].lower()), None)
    assert relocate_q is not None
    assert relocate_q["round_number"] == 4
    assert relocate_q["category"] == "HR"

    # Verify Technical Interview questions belong to Round 3 / Category Technical
    poly_q = next((d for d in q_details if "what is polymorphism" in d["question"].lower()), None)
    assert poly_q is not None
    assert poly_q["round_number"] == 3
    assert poly_q["category"] == "Technical"

    # Verify "Included" is NOT extracted as a topic
    topics = info["topics"]
    assert "Included" not in topics
    assert "Process" not in topics


# ==============================================================================
# 3. UNICODE DASH AND BULLET HEADERS
# ==============================================================================

def test_unicode_dash_and_bullet_headers():
    text = (
        "Company: Cognizant\n"
        "Round 1 – Aptitude Assessment\n"
        "• Percentages\n"
        "• Number Series\n"
        "Round 2 — Technical Interview\n"
        "1. What is indexing in DBMS?\n"
        "Round 3 - HR Interview\n"
        "- Tell me about your final year project."
    )
    info = extract_information(clean_message(text))
    rounds = info["rounds"]
    assert len(rounds) == 3

    assert rounds[0]["round_number"] == 1
    assert rounds[0]["round_type"] == "Aptitude"

    assert rounds[1]["round_number"] == 2
    assert rounds[1]["round_type"] == "Technical"

    assert rounds[2]["round_number"] == 3
    assert rounds[2]["round_type"] == "HR"


# ==============================================================================
# 4. IMPERATIVE PROGRAMMING QUESTION STARTERS
# ==============================================================================

def test_imperative_coding_question_verbs():
    text = (
        "Coding Round Questions:\n"
        "1. Swap two numbers without third variable.\n"
        "2. Print binary tree in zigzag order.\n"
        "3. Sort an array of 0s, 1s and 2s.\n"
        "4. Reverse a singly linked list.\n"
        "5. Count set bits in an integer.\n"
        "6. Check if string is rotation of another string.\n"
        "7. Convert infix to postfix expression.\n"
        "8. Implement stack using queues.\n"
        "9. Merge two sorted arrays.\n"
    )
    questions = extract_questions(clean_message(text))
    q_lower = [q.lower() for q in questions]

    assert any("swap two numbers" in q for q in q_lower)
    assert any("print binary tree" in q for q in q_lower)
    assert any("sort an array" in q for q in q_lower)
    assert any("reverse a singly linked list" in q for q in q_lower)
    assert any("count set bits" in q for q in q_lower)
    assert any("check if string is rotation" in q for q in q_lower)
    assert any("convert infix to postfix" in q for q in q_lower)
    assert any("implement stack using queues" in q for q in q_lower)
    assert any("merge two sorted arrays" in q for q in q_lower)


# ==============================================================================
# 5. COMPOUND QUESTIONS PRESERVATION
# ==============================================================================

def test_compound_questions_not_split():
    text = (
        "Technical Questions:\n"
        "What is Java and why is it platform independent?\n"
        "Explain OOP and how it differs from procedural programming?\n"
        "What is an index and when should you avoid using it in SQL?\n"
    )
    questions = extract_questions(clean_message(text))
    assert len(questions) == 3
    assert "What is Java and why is it platform independent?" in questions
    assert "Explain OOP and how it differs from procedural programming?" in questions
    assert "What is an index and when should you avoid using it in SQL?" in questions


# ==============================================================================
# 6. FALSE POSITIVE "PROCESS" FILTERING
# ==============================================================================

def test_recruitment_process_not_extracted_as_os_process_topic():
    text = (
        "Company: Infosys\n"
        "Role: Specialist Programmer\n"
        "Recruitment Process:\n"
        "Round 1: Online Test\n"
        "Interview Process was smooth.\n"
        "Selection Process completed in two weeks."
    )
    info = extract_information(clean_message(text))
    assert "Process" not in info["topics"]
    assert "Operating System" not in info["topics"]


# ==============================================================================
# 7. UNAMBIGUOUS VS AMBIGUOUS ROUND HEADINGS
# ==============================================================================

def test_missing_round_headings_leaves_round_none():
    text = (
        "Company: Wipro\n"
        "They asked what is polymorphism?\n"
        "Also asked to reverse a string."
    )
    info = extract_information(clean_message(text))
    # No round heading was present in text
    assert len(info["rounds"]) == 0
    # Questions should have round_number as None, not guessed
    for qd in info["question_details"]:
        assert qd["round_number"] is None


# ==============================================================================
# 8. DUPLICATE DETECTION DISTINCTION
# ==============================================================================

def test_duplicate_detection_distinguishes_different_questions():
    q1 = "What is an abstract class in Java?"
    q2 = "What is an interface in Java?"
    sim = calculate_similarity(q1, q2)
    # They share 5 words but are fundamentally different questions
    assert sim < 0.75, f"Similarity {sim} should be below threshold 0.75"
    assert not is_duplicate(q1, [q2])["duplicate"]


# ==============================================================================
# 9. CROSS CATEGORY ISOLATION
# ==============================================================================

def test_cross_category_isolation():
    text = (
        "Company: Accenture\n"
        "Round 1: Aptitude Test\n"
        "Topics: Percentages, Profit and Loss\n"
        "Round 2: HR Interview\n"
        "Questions: Are you willing to relocate? What are your hobbies?"
    )
    info = extract_information(clean_message(text))
    for topic_detail in info["topic_details"]:
        assert topic_detail["category"] in {"Aptitude", "Quantitative Aptitude"}
        assert topic_detail["category"] != "Technical"

    for question_detail in info["question_details"]:
        assert question_detail["category"] == "HR"
        assert question_detail["category"] != "Technical"
        assert question_detail["round_number"] == 2

