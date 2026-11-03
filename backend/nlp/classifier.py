import re


CATEGORIES = {
    "Eligibility": [
        "eligibility",
        "eligible",
        "cgpa",
        "backlog",
        "backlogs",
        "percentage",
        "qualification",
    ],

    "Communication": [
        "communication",
        "reading comprehension",
        "grammar",
        "vocabulary",
        "verbal ability",
        "communication assessment",
        "communication round",
    ],

    "Aptitude": [
        "aptitude",
        "quantitative",
        "logical reasoning",
        "verbal ability",
        "reasoning",
        "online assessment",
        "percentages",
        "profit and loss",
        "ratio",
        "probability",
        "time and work",
    ],

    "Coding": [
        "coding",
        "programming",
        "array",
        "arrays",
        "string",
        "strings",
        "leetcode",
        "algorithm",
        "data structure",
        "linked list",
        "stack",
        "queue",
        "tree",
        "graph",
        "dynamic programming",
        "recursion",
    ],

    "Technical": [
        "technical interview",
        "technical",
        "dbms",
        "sql",
        "oops",
        "oop",
        "object oriented programming",
        "operating system",
        "computer networks",
        "thread",
        "deadlock",
        "java",
        "python",
        "c++",
    ],

    "HR": [
        "hr",
        "human resources",
        "strengths",
        "weaknesses",
        "relocation",
        "salary",
        "tell me about yourself",
        "about yourself",
        "career goals",
        "hobbies",
    ],

    "Interview Experience": [
        "interview experience",
        "experience",
        "interview",
        "asked",
        "asked to",
    ],

    "Selection": [
        "selected",
        "selection",
        "offer",
        "placed",
    ],

    "Rejection": [
        "rejected",
        "rejection",
        "not selected",
        "eliminated",
    ],

    "Company Information": [
        "company",
        "job role",
        "package",
        "ctc",
    ],
}


def classify_message(text: str):
    if not text:
        return []

    text_lower = text.lower()
    detected_categories = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            pattern = rf"(?<![a-z0-9]){re.escape(keyword.lower())}(?![a-z0-9])"
            if re.search(pattern, text_lower):
                if category not in detected_categories:
                    detected_categories.append(category)
                break

    return detected_categories
