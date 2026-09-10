import re


CATEGORIES = {
    "Eligibility": [
        "eligibility",
        "eligible",
        "cgpa",
        "backlog",
        "backlogs",
        "percentage",
        "qualification"
    ],

    "Aptitude": [
        "aptitude",
        "quantitative",
        "logical reasoning",
        "verbal ability",
        "reasoning",
        "assessment",
        "online assessment"
    ],

    "Coding": [
        "coding",
        "programming",
        "array",
        "arrays",
        "string",
        "strings",
        "leetcode",
        "problem",
        "algorithm",
        "data structure",
        "linked list",
        "stack",
        "queue",
        "tree",
        "graph"
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
        "os",
        "process",
        "thread",
        "network",
        "java",
        "python",
        "c++"
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
        "career goals"
    ],

    "Interview Experience": [
        "interview experience",
        "experience",
        "interview",
        "asked",
        "asked to",
        "question",
        "questions"
    ],

    "Selection": [
        "selected",
        "selection",
        "offer",
        "placed"
    ],

    "Rejection": [
        "rejected",
        "rejection",
        "not selected",
        "eliminated"
    ],

    "Company Information": [
        "company",
        "job role",
        "package",
        "salary",
        "recruitment"
    ]
}


def classify_message(text: str):

    text_lower = text.lower()
    detected_categories = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text_lower and category not in detected_categories:
                detected_categories.append(category)
                break

    return detected_categories