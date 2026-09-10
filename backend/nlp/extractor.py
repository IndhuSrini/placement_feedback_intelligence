import re


TOPIC_ALIASES = {
    "arrays": "Arrays",
    "array": "Arrays",
    "strings": "Strings",
    "string": "Strings",
    "linked list": "Linked List",
    "linkedlist": "Linked List",
    "stack": "Stack",
    "queue": "Queue",
    "tree": "Tree",
    "graph": "Graph",
    "recursion": "Recursion",
    "dynamic programming": "Dynamic Programming",
    "sorting": "Sorting",
    "searching": "Searching",
    "hashing": "Hashing",
    "binary search": "Binary Search",
    "greedy": "Greedy",
    "oops": "OOP",
    "oop": "OOP",
    "object oriented programming": "OOP",
    "dbms": "DBMS",
    "normalization": "DBMS",
    "sql": "SQL",
    "joins": "Joins",
    "join": "Joins",
    "operating system": "Operating System",
    "os": "Operating System",
    "process": "Process",
    "thread": "Thread",
    "deadlock": "Deadlock",
    "computer networks": "Computer Networks",
    "tcp/ip": "TCP/IP",
    "tcp": "TCP/IP",
    "http": "HTTP",
    "api": "API",
    "java": "Java",
    "python": "Python",
    "c++": "C++",
    "data structures": "Data Structures",
    "quantitative aptitude": "Quantitative Aptitude",
    "percentages": "Percentages",
    "profit and loss": "Profit and Loss",
    "ratio": "Ratio",
    "probability": "Probability",
    "time and work": "Time and Work",
    "time speed distance": "Time Speed Distance",
    "logical reasoning": "Logical Reasoning",
    "verbal ability": "Verbal Ability",
    "strengths": "Strengths",
    "weaknesses": "Weaknesses",
    "introduction": "Introduction",
    "tell me about yourself": "Tell Me About Yourself",
    "about yourself": "Tell Me About Yourself",
    "relocation": "Relocation",
    "salary": "Salary",
    "career goals": "Career Goals"
}


def normalize_topic_name(topic_name: str):
    if not topic_name:
        return None

    text = str(topic_name).strip()
    if not text:
        return None

    lowered = text.lower()
    if lowered in TOPIC_ALIASES:
        return TOPIC_ALIASES[lowered]

    for alias, canonical in TOPIC_ALIASES.items():
        if alias in lowered:
            return canonical

    return re.sub(r"\s+", " ", text).title()


def normalize_difficulty(value: str):
    if not value:
        return None

    lowered = value.lower().strip()
    if "very easy" in lowered or "easy" in lowered:
        return "Easy"
    if "moderate" in lowered or "medium" in lowered:
        return "Medium"
    if "hard" in lowered or "difficult" in lowered or "very hard" in lowered:
        return "Hard"
    return None


def infer_round_type(text: str):
    lower = text.lower()

    if "aptitude" in lower or "quantitative" in lower or "logical" in lower or "verbal" in lower:
        return "Aptitude"
    if "coding" in lower or "programming" in lower or "algorithm" in lower:
        return "Coding"
    if "technical" in lower or "dbms" in lower or "sql" in lower or "java" in lower or "python" in lower or "network" in lower:
        return "Technical"
    if "hr" in lower or "strength" in lower or "weakness" in lower or "relocation" in lower or "salary" in lower:
        return "HR"
    if "group discussion" in lower or "gd" in lower:
        return "Group Discussion"
    if "managerial" in lower:
        return "Managerial"
    if "assessment" in lower or "online assessment" in lower:
        return "Aptitude"
    if "interview" in lower:
        return "Technical"
    return "Unknown"


def extract_cgpa(text: str):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*cgpa",
        r"cgpa\s*(?:of|:)?\s*(\d+(?:\.\d+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def extract_backlogs(text: str):
    patterns = [
        r"(\d+)\s*(?:active\s*)?backlogs?",
        r"backlogs?\s*(?:of|:)?\s*(\d+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    if re.search(r"no\s+(?:active\s+)?backlogs?", text, re.IGNORECASE):
        return 0

    return None


def extract_rounds(text: str):
    rounds = []
    seen_keys = set()

    def add_round(round_number, round_type, description):
        if not round_type or round_type == "Unknown":
            return

        if round_number is not None:
            key = (round_number, round_type.lower())
            if key in seen_keys:
                return
        else:
            if any(existing.get("round_type", "").lower() == round_type.lower() and existing.get("round_number") is not None for existing in rounds):
                return
            key = (None, round_type.lower())
            if key in seen_keys:
                return

        rounds.append({
            "round_number": round_number,
            "round_type": round_type,
            "description": description
        })
        seen_keys.add(key)

    explicit_number_patterns = [
        r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th)\s+(?:round|rounds)\s+(?:and\s+)?(?:aptitude|coding|technical|hr|managerial|group discussion|online assessment|assessment|interview)\b",
        r"\b(?:aptitude|coding|technical|hr|managerial|group discussion|online assessment|assessment)\s+round\b",
        r"\b(?:technical|hr)\s+interview\b",
    ]

    for pattern in explicit_number_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matched = match.group(0).strip()
            lower = matched.lower()

            if re.search(r"first|1st", lower):
                number = 1
            elif re.search(r"second|2nd", lower):
                number = 2
            elif re.search(r"third|3rd", lower):
                number = 3
            elif re.search(r"fourth|4th", lower):
                number = 4
            elif re.search(r"fifth|5th", lower):
                number = 5
            elif re.search(r"sixth|6th", lower):
                number = 6
            elif re.search(r"seventh|7th", lower):
                number = 7
            elif re.search(r"eighth|8th", lower):
                number = 8
            elif re.search(r"ninth|9th", lower):
                number = 9
            elif re.search(r"tenth|10th", lower):
                number = 10
            else:
                number = None

            round_type = infer_round_type(matched)
            if "interview" in lower and "technical" in lower:
                round_type = "Technical"
            if "hr" in lower and "interview" in lower:
                round_type = "HR"

            if number is None and round_type.lower() == "technical":
                if any(existing.get("round_type") == "Technical" and existing.get("round_number") is not None for existing in rounds):
                    continue
            if number is None and round_type.lower() == "coding":
                if any(existing.get("round_type") == "Coding" and existing.get("round_number") is not None for existing in rounds):
                    continue
            if number is None and round_type.lower() == "hr":
                if any(existing.get("round_type") == "HR" and existing.get("round_number") is not None for existing in rounds):
                    continue

            add_round(number, round_type, matched)

    if not any(existing.get("round_type") == "Technical" and existing.get("round_number") is not None for existing in rounds) and re.search(r"\btechnical interview\b", text, re.IGNORECASE):
        add_round(None, "Technical", "Technical interview")
    if not any(existing.get("round_type") == "HR" and existing.get("round_number") is not None for existing in rounds) and re.search(r"\bhr\b.*\basked\b|\basked\b.*\bhr\b", text, re.IGNORECASE):
        add_round(None, "HR", "HR asked")

    rounds.sort(key=lambda each: (each["round_number"] is None, each["round_number"] if each["round_number"] is not None else 999))
    return rounds


def extract_topics(text: str):
    lower_text = text.lower()
    found_topics = []

    if "process" in lower_text or "thread" in lower_text:
        if "operating system" not in lower_text and "os" not in lower_text:
            found_topics.append("Operating System")

    for alias, canonical in TOPIC_ALIASES.items():
        if alias in lower_text and canonical not in found_topics:
            found_topics.append(canonical)

    return found_topics


def extract_difficulty(text: str):
    found = []
    normalized_text = text.lower()

    for phrase, canonical in [
        ("very easy", "Easy"),
        ("easy", "Easy"),
        ("moderate", "Medium"),
        ("medium", "Medium"),
        ("hard", "Hard"),
        ("very hard", "Hard"),
        ("difficult", "Hard")
    ]:
        pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
        if re.search(pattern, normalized_text) and canonical not in found:
            found.append(canonical)

    return found


def normalize_question_text(question: str):
    text = str(question).strip()
    if not text:
        return ""

    text = re.sub(r"^(?:technical\s+interview|interview|hr|they|he|she|interviewer|candidate)\s+asked\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(?:they|he|she|interviewer|hr|candidate)\s+asked\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(?:asked\s+to|asked\s+about|question\s+is|question\s+was|question\s*:\s*)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(?:coding|technical|aptitude|hr)\s+(?:question|round)\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^\s*[-*•]\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .;:!?()[]{}\"'")

    if not text:
        return ""

    if text and not re.search(r"[?]$", text):
        text += "?"

    return text


def extract_questions(text: str):
    questions = []
    seen = set()

    question_keywords = [
        "asked",
        "explain",
        "difference between",
        "what is",
        "why",
        "how",
        "solve",
        "find",
        "implement",
        "write a program",
        "tell me about yourself",
        "strengths",
        "weaknesses",
        "relocation",
        "salary",
        "reverse",
        "duplicate elements",
        "interviewer asked",
        "they asked",
        "hr asked",
        "coding question",
        "technical question",
        "aptitude question"
    ]

    def add_candidate(candidate: str):
        if not candidate:
            return
        candidate = normalize_question_text(candidate)
        if not candidate:
            return
        if len(candidate.split()) < 2:
            return
        if any(skip in candidate.lower() for skip in ["first round", "second round", "third round", "coding round", "aptitude round", "technical round", "hr round", "group discussion"]):
            return
        lower_candidate = candidate.lower()
        if "strengths" in lower_candidate or "weaknesses" in lower_candidate:
            if "tell me about yourself" not in lower_candidate:
                return
        if lower_candidate not in seen:
            questions.append(candidate)
            seen.add(lower_candidate)

    def split_sentence_fragments(sentence: str):
        fragments = [sentence.strip()]
        split_on = re.compile(r"\s+and\s+(?=(?:explain|difference|find|reverse|tell|are|what|why|how|solve|implement|write|do|can|should|would)\b)", re.IGNORECASE)
        comma_split = re.compile(r",\s*(?=(?:strengths|weaknesses|salary|relocation|experience|career goals)\b)", re.IGNORECASE)
        new_fragments = []
        for fragment in fragments:
            for part in split_on.split(fragment):
                clean_part = part.strip()
                if clean_part:
                    for subpart in comma_split.split(clean_part):
                        if subpart.strip():
                            new_fragments.append(subpart.strip())
        return new_fragments

    sentences = re.split(r"(?<=[.?])\s+|\n+", text)
    for sentence in sentences:
        clean_sentence = sentence.strip()
        if not clean_sentence:
            continue

        lower_sentence = clean_sentence.lower()
        if not any(keyword in lower_sentence for keyword in question_keywords):
            continue

        if any(phrase in lower_sentence for phrase in ["first round", "second round", "third round", "round was", "round had"]):
            continue

        for fragment in split_sentence_fragments(clean_sentence):
            for part in re.split(r"\?|\.(?!\d)|;", fragment):
                add_candidate(part)

    direct_commands = [
        "reverse a string",
        "find duplicate elements in an array",
        "explain normalization in dbms",
        "difference between process and thread",
        "tell me about yourself",
        "why should we hire you",
        "are you willing to relocate",
        "what is the difference between process and thread"
    ]
    for command in direct_commands:
        if command in text.lower():
            add_candidate(command)

    filtered = []
    for question in questions:
        lower_question = question.lower()
        if " and " in lower_question:
            markers = ["explain", "difference between", "find", "reverse", "tell me about yourself", "are you willing to relocate"]
            if sum(1 for marker in markers if marker in lower_question) > 1:
                continue
        if lower_question.startswith("hr asked ") or lower_question.startswith("technical interview asked "):
            continue
        filtered.append(question)

    return filtered


def extract_information(text: str):
    return {
        "minimum_cgpa": extract_cgpa(text),
        "maximum_backlogs": extract_backlogs(text),
        "rounds": extract_rounds(text),
        "topics": extract_topics(text),
        "difficulty": extract_difficulty(text),
        "questions": extract_questions(text)
    }