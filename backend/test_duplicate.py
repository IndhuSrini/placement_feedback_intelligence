from nlp.duplicate_detector import is_duplicate


existing_questions = [
    "What is normalization in DBMS?",
    "Explain operating system process scheduling",
    "What is polymorphism in Java?"
]


new_question = "They asked about DBMS normalization"


result = is_duplicate(
    new_question,
    existing_questions
)


print(result)