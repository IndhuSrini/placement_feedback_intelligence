
import re


# =========================================================
# CONSTANTS
# =========================================================

COMPANY_BOUNDARY_WORDS = [
    "round",
    "rounds",
    "stage",
    "technical",
    "coding",
    "communication",
    "aptitude",
    "hr",
    "questions",
    "question",
    "difficulty",
    "feedback",
    "eligibility",
    "package",
    "role",
    "experience",
    "drive",
    "placement",
    "interview",
    "hiring",
    "batch",
    "topic",
    "topics",
    "recruitment",
]


TOPIC_ALIASES = {
    "arrays": "Arrays",
    "array": "Arrays",
    "strings": "Strings",
    "string": "Strings",
    "longest substring": "Strings",
    "substring": "Strings",
    "linked list": "Linked List",
    "linkedlist": "Linked List",
    "stack": "Stack",
    "stacks": "Stack",
    "queue": "Queue",
    "queues": "Queue",
    "tree": "Tree",
    "trees": "Tree",
    "graph": "Graph",
    "graphs": "Graph",
    "recursion": "Recursion",
    "dynamic programming": "Dynamic Programming",
    "sorting": "Sorting",
    "searching": "Searching",
    "hashing": "Hashing",
    "binary search": "Binary Search",
    "greedy": "Greedy",
    "algorithm": "Algorithms",
    "algorithms": "Algorithms",
    "oops": "OOP",
    "oop": "OOP",
    "object oriented programming": "OOP",
    "abstract class": "OOP",
    "interface": "OOP",
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
    "rest api": "REST API",
    "api": "API",
    "microservices": "Microservices",
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
    "career goals": "Career Goals",
}


QUESTION_STARTERS = (
    "self|explain|what|why|how|which|when|where|who|can|could|"
    "would|should|do|did|does|write|find|check|list|describe|"
    "name|difference|method|puzzle|tell|solve|implement|code|"
    "coding|features|compare|is|are|was|were"
)


INCOMPLETE_ENDINGS = {
    "to",
    "the",
    "a",
    "an",
    "of",
    "for",
    "with",
    "between",
    "when",
    "where",
    "which",
    "that",
    "and",
    "or",
    "whether",
    "if",
    "from",
    "in",
    "on",
    "about",
    "into",
    "as",
    "than",
    "by",
}


# =========================================================
# GENERAL NORMALIZATION
# =========================================================

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

    if (
        "very hard" in lowered
        or "hard" in lowered
        or "difficult" in lowered
    ):
        return "Hard"

    return None


def normalize_company_name(name: str):
    if not name:
        return None

    cleaned = str(name).strip()

    cleaned = re.sub(
        r"^company\s*[:\-]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )

    cleaned = cleaned.strip(" .;:-")
    cleaned = re.sub(r"\s+", " ", cleaned)

    if not cleaned:
        return None

    canonical_names = {
        "tcs": "TCS",
        "infosys": "Infosys",
        "cognizant": "Cognizant",
        "accenture": "Accenture",
        "capgemini": "Capgemini",
        "wipro": "Wipro",
        "zoho": "Zoho",
        "freshworks": "Freshworks",
        "hcltech": "HCLTech",
        "ibm": "IBM",
        "tech mahindra": "Tech Mahindra",
        "deloitte": "Deloitte",
        "tata consultancy services": "Tata Consultancy Services",
        "ust": "UST",
        "mphasis": "Mphasis",
        "hexaware": "Hexaware",
        "persist": "Persist",
        "microsoft": "Microsoft",
        "google": "Google",
        "amazon": "Amazon",
        "meta": "Meta",
        "mistral": "Mistral",
        "econ systems": "Econ Systems",
    }

    lowered = cleaned.lower()

    if lowered in canonical_names:
        return canonical_names[lowered]

    if re.fullmatch(r"[A-Z0-9&.-]+", cleaned):
        return cleaned

    parts = cleaned.split()
    fixed = []

    for part in parts:
        if re.fullmatch(r"[A-Za-z0-9&.-]+", part):
            if part.isupper() and len(part) <= 5:
                fixed.append(part)
            else:
                fixed.append(
                    part[0].upper() + part[1:].lower()
                    if part and part[0].isalpha()
                    else part
                )
        else:
            fixed.append(part)

    return " ".join(fixed)


def strip_field_prefixes(value: str):
    if not value:
        return ""

    text = str(value).strip()

    while True:
        match = re.match(
            r"^(?:company|rounds?|stage|question|questions|"
            r"difficulty|feedback|role|package|eligibility|"
            r"code|dept|department|l1|l2)\s*[:\-]?\s*",
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            return text.strip()

        text = text[match.end():].strip()


# =========================================================
# COMPANY
# =========================================================

def extract_company_name(text: str):
    """
    Supports:

    Company: Infosys
    Company : Accenture
    Company: Cognizant
    2. Company: Infosys
    """

    if not text:
        return None

    patterns = [
        r"(?:^|\n)\s*\d+\.\s*company\s*[:\-]\s*([^\n]+)",
        r"(?:^|\n)\s*company\s*[:\-]\s*([^\n]+)",
        r"\bcompany\s*[:\-]\s*([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        candidate = match.group(1).strip()

        boundary_pattern = (
            r"\s+(?:"
            + "|".join(
                re.escape(word)
                for word in COMPANY_BOUNDARY_WORDS
            )
            + r")\s*[:\-]?"
        )

        candidate = re.split(
            boundary_pattern,
            candidate,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        candidate = candidate.strip(" .;:-")

        if candidate:
            return normalize_company_name(candidate)

    return None


# =========================================================
# ROLE
# =========================================================

def extract_role(text: str):
    if not text:
        return None

    patterns = [
        r"(?:^|\n)\s*\d+\.\s*role\s*[:\-]\s*([^\n]+)",
        r"(?:^|\n)\s*role\s*[:\-]\s*([^\n]+)",
        r"\b(?:hiring|drive)\s+for\s+([A-Za-z][A-Za-z0-9 /&.-]+?)(?=\s+(?:in|for|the)\s+2023|\s+for\s+the\s+2023|[.,\n]|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        value = match.group(1).strip()

        value = re.split(
            r"\s+(?:eligibility|round|rounds|difficulty|"
            r"topic|topics|question|questions)\s*[:\-]",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        value = value.strip(" .;:-")

        if value:
            return value

    return None


# =========================================================
# ROUND EXTRACTION
# =========================================================

def infer_round_type(text: str):
    lower = text.lower().strip()

    if "communication" in lower:
        return "Communication"

    if (
        "aptitude" in lower
        or "quantitative" in lower
        or "logical" in lower
        or "verbal" in lower
    ):
        return "Aptitude"

    if (
        "coding" in lower
        or "programming" in lower
        or "algorithm" in lower
    ):
        return "Coding"

    # IMPORTANT:
    # System Design must come before generic Technical.
    if "system design" in lower:
        return "System Design"

    if "managerial" in lower:
        return "Managerial"

    if (
        "technical" in lower
        or "dbms" in lower
        or "sql" in lower
        or "java" in lower
        or "python" in lower
        or "network" in lower
    ):
        return "Technical"

    if (
        re.search(r"\bhr\b", lower)
        or "strength" in lower
        or "weakness" in lower
        or "relocation" in lower
        or "salary" in lower
    ):
        return "HR"

    if (
        "group discussion" in lower
        or re.search(r"\bgd\b", lower)
    ):
        return "Group Discussion"

    if "written test" in lower or lower == "written":
        return "Written Test"

    if "presentation" in lower:
        return "Presentation"

    if "case study" in lower:
        return "Case Study"

    if "behavioral" in lower:
        return "Behavioral"

    if (
        "assessment" in lower
        or "online assessment" in lower
    ):
        return "Aptitude"

    if "interview" in lower:
        return "Interview"

    return "Unknown"


def extract_rounds(text: str):
    if not text:
        return []

    rounds = []
    seen = set()

    def add_round(round_number, round_type, description):
        if not round_type or round_type == "Unknown":
            return

        key = (
            round_number,
            round_type.lower(),
        )

        if key in seen:
            return

        rounds.append(
            {
                "round_number": round_number,
                "round_type": round_type,
                "description": description,
            }
        )

        seen.add(key)

    def parse_number(value):
        if not value:
            return None

        value = value.lower().strip()

        mapping = {
            "first": 1,
            "1st": 1,
            "1": 1,
            "second": 2,
            "2nd": 2,
            "2": 2,
            "third": 3,
            "3rd": 3,
            "3": 3,
            "fourth": 4,
            "4th": 4,
            "4": 4,
            "fifth": 5,
            "5th": 5,
            "5": 5,
            "sixth": 6,
            "6th": 6,
            "6": 6,
            "seventh": 7,
            "7th": 7,
            "7": 7,
            "eighth": 8,
            "8th": 8,
            "8": 8,
            "ninth": 9,
            "9th": 9,
            "9": 9,
            "tenth": 10,
            "10th": 10,
            "10": 10,
        }

        return mapping.get(value)

    # ---------------------------------------------------------
    # Numbered rounds
    # ---------------------------------------------------------

    numbered_patterns = [
        r"\bround\s*(?:no\.?|number)?\s*(\d+)\s*[:\-]?\s*([A-Za-z][A-Za-z ]*)",
        r"\b(\d+)(?:st|nd|rd|th)\s+round\s*[:\-]?\s*([A-Za-z][A-Za-z ]*)",
        r"\b(first|second|third|fourth|fifth|sixth|seventh|"
        r"eighth|ninth|tenth)\s+round\s*[:\-]?\s*([A-Za-z][A-Za-z ]*)",
    ]

    for pattern in numbered_patterns:
        for match in re.finditer(
            pattern,
            text,
            re.IGNORECASE,
        ):
            round_number = parse_number(match.group(1))
            label = match.group(2).strip()

            label = re.split(
                r"\s+(?:and|was|is|are|had|with|question|"
                r"questions|difficulty|feedback|role|eligibility|"
                r"topic|topics)\b",
                label,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip(" .;:-")

            round_type = infer_round_type(label)

            if round_type != "Unknown":
                add_round(
                    round_number,
                    round_type,
                    label,
                )

    # ---------------------------------------------------------
    # Round flow
    # ---------------------------------------------------------

    flow_patterns = [
        r"\bround\s*flow\s*[:\-]\s*([^\n]+)",
        r"\brounds?\s*[:\-]\s*([^\n]+)",
        r"\binterview\s*flow\s*[:\-]\s*([^\n]+)",
    ]

    for pattern in flow_patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if not match:
            continue

        value = match.group(1)

        value = re.split(
            r"\s+(?:difficulty|topic|topics|question|"
            r"questions|eligibility|package|recruitment)\s*[:\-]",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        parts = re.split(
            r",|->|>|/",
            value,
        )

        next_number = 1

        for part in parts:
            label = part.strip(" .;:-")

            if not label:
                continue

            round_type = infer_round_type(label)

            if round_type == "Unknown":
                continue

            add_round(
                next_number,
                round_type,
                label,
            )

            next_number += 1

    # ---------------------------------------------------------
    # Generic stage mentions
    # ---------------------------------------------------------

    stage_patterns = [
        ("Aptitude", r"\baptitude\b"),
        ("Coding", r"\bcoding\b"),
        ("Technical", r"\btechnical\s+interview\b"),
        ("System Design", r"\bsystem\s+design\b"),
        ("HR", r"\bhr\s+round\b"),
        ("Communication", r"\bcommunication\b"),
        ("Managerial", r"\bmanagerial\s+interview\b"),
        ("Group Discussion", r"\bgroup\s+discussion\b"),
        ("Written Test", r"\bwritten\s+test\b"),
    ]

    for round_type, pattern in stage_patterns:
        if re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            already_present = any(
                item["round_type"].lower()
                == round_type.lower()
                for item in rounds
            )

            if not already_present:
                add_round(
                    None,
                    round_type,
                    round_type,
                )

    rounds.sort(
        key=lambda item: (
            item["round_number"] is None,
            item["round_number"]
            if item["round_number"] is not None
            else 999,
        )
    )

    return rounds


# =========================================================
# ELIGIBILITY
# =========================================================

def extract_cgpa(text: str):
    if not text:
        return None

    patterns = [
        r"(\d+(?:\.\d+)?)\s*cgpa",
        r"cgpa\s*(?:of|:)?\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return float(match.group(1))

    return None


def extract_backlogs(text: str):
    if not text:
        return None

    patterns = [
        r"(\d+)\s*(?:active\s*)?backlogs?",
        r"backlogs?\s*(?:of|:)?\s*(\d+)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return int(match.group(1))

    if re.search(
        r"no\s+(?:active\s+)?backlogs?",
        text,
        re.IGNORECASE,
    ):
        return 0

    if re.search(
        r"no\s+standing\s+arrears",
        text,
        re.IGNORECASE,
    ):
        return 0

    return None


# =========================================================
# TOPICS
# =========================================================

def extract_topics(text: str):
    if not text:
        return []

    lower_text = text.lower()
    found_topics = []

    def add_topic(topic):
        if topic not in found_topics:
            found_topics.append(topic)

    if re.search(
        r"\boperating system\b",
        lower_text,
    ):
        add_topic("Operating System")

    if (
        re.search(r"\bprocess\b", lower_text)
        and re.search(r"\bthread\b", lower_text)
        and (
            re.search(r"\bos\b", lower_text)
            or re.search(
                r"\boperating system\b",
                lower_text,
            )
        )
    ):
        add_topic("Operating System")

    if "longest substring" in lower_text:
        add_topic("Strings")
        add_topic("Algorithms")

    if (
        "second highest salary" in lower_text
        or "highest salary" in lower_text
    ):
        add_topic("SQL")
        add_topic("DBMS")

    if (
        "abstract class" in lower_text
        or "interface" in lower_text
        or re.search(r"\boop\b", lower_text)
        or re.search(r"\boops\b", lower_text)
    ):
        add_topic("OOP")

    if "rest api" in lower_text:
        add_topic("REST API")

    if "microservices" in lower_text:
        add_topic("Microservices")

    for alias, canonical in TOPIC_ALIASES.items():
        if alias in {
            "operating system",
            "os",
        }:
            continue

        boundary_pattern = (
            rf"(?<![a-z]){re.escape(alias)}(?![a-z])"
        )

        if re.search(
            boundary_pattern,
            lower_text,
        ):
            add_topic(canonical)

    return found_topics


# =========================================================
# DIFFICULTY
# =========================================================

def extract_difficulty(text: str):
    if not text:
        return []

    found = []
    normalized_text = text.lower()

    values = [
        ("very easy", "Easy"),
        ("easy", "Easy"),
        ("moderate", "Medium"),
        ("medium", "Medium"),
        ("very hard", "Hard"),
        ("hard", "Hard"),
        ("difficult", "Hard"),
    ]

    for phrase, canonical in values:
        pattern = (
            rf"(?<!\w){re.escape(phrase)}(?!\w)"
        )

        if re.search(
            pattern,
            normalized_text,
        ):
            if canonical not in found:
                found.append(canonical)

    if not found:
        return ["Medium"]

    return found


# =========================================================
# QUESTION VALIDATION
# =========================================================

def _is_fragment_question(candidate: str) -> bool:
    if not candidate:
        return True

    text = str(candidate).strip()

    text = text.strip(
        " .;:!?(),[]{}\\\"'"
    )

    if not text:
        return True

    lower = text.lower()

    # Single generic words.
    if re.fullmatch(
        r"(?:s|l1|l2|what|why|how|explain|write|do|did|"
        r"does|can|would|should|which|who|when|where|self|"
        r"code|coding|find|check|list|describe|name|difference|"
        r"method|puzzle|feature|features)",
        lower,
    ):
        return True

    # Generic incomplete phrases.
    if re.fullmatch(
        r"(?:what\s+is\s+(?:the|a|an))",
        lower,
    ):
        return True

    if re.fullmatch(
        r"(?:difference\s+between)",
        lower,
    ):
        return True

    words = lower.split()

    if len(words) < 2:
        return True

    # Protect against incomplete endings.
    if words[-1] in INCOMPLETE_ENDINGS:
        return True

    incomplete_patterns = [
        r"^write\s+(?:a|an|the)?\s*(?:program|code|query)?\s*$",
        r"^explain\s+(?:the|a|an)\s*$",
        r"^check\s+whether\s*$",
        r"^check\s+if\s*$",
        r"^how\s+would\s+you\s+approach\s*$",
        r"^what\s+is\s*$",
        r"^what\s+are\s*$",
        r"^why\s+is\s*$",
        r"^why\s+are\s*$",
        r"^difference\s+between\s*$",
    ]

    for pattern in incomplete_patterns:
        if re.fullmatch(
            pattern,
            lower,
        ):
            return True

    return False


def normalize_question_text(question: str):
    if not question:
        return ""

    text = str(question).strip()

    # Remove numbered-list prefixes.
    text = re.sub(
        r"^\s*\d+\s*[\.\):\-]\s*",
        "",
        text,
    )

    # Remove bullet characters.
    text = re.sub(
        r"^\s*[-*•]\s*",
        "",
        text,
    )

    # Remove common prefixes.
    text = re.sub(
        r"^(?:technical\s+interview|interview|hr|they|he|she|"
        r"interviewer|candidate)\s+asked\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(?:asked\s+to|asked\s+about|question\s+is|"
        r"question\s+was)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(?:coding|technical|aptitude|hr)\s+"
        r"(?:question|round)\s*[:\-]?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(?:l1|l2|code|coding|questions?|technical\s+interview)"
        r"\s*[:\-]?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Fix accidental internal question marks.
    text = re.sub(
        r"\?\s+(?=[a-z])",
        " ",
        text,
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    text = text.strip(
        " .;:!?(),[]{}\\\"'"
    )

    if not text:
        return ""

    if _is_fragment_question(text):
        return ""

    if "l1?" in text.lower() or "l2?" in text.lower():
        return ""

    if len(text.split()) < 2:
        return ""

    if not text.endswith("?"):
        text += "?"

    return text


def split_question_items(text: str):
    if not text:
        return []

    normalized = str(text).strip()

    # Remove question-list labels.
    normalized = re.sub(
        r"\b(?:l1\s*,?\s*l2|l2\s*,?\s*l1)"
        r"\s*questions?\s*[:\-]?\s*",
        " ",
        normalized,
        flags=re.IGNORECASE,
    )

    normalized = re.sub(
        r"\b(?:technical\s+interview\s+)?"
        r"questions?\s*[:\-]?\s*",
        " ",
        normalized,
        flags=re.IGNORECASE,
    )

    # Newlines are safe boundaries.
    normalized = re.sub(
        r"\s*\n+\s*",
        " | ",
        normalized,
    )

    # Existing | separators.
    normalized = re.sub(
        r"\s*\|\s*",
        " | ",
        normalized,
    )

    # Split AFTER ? only when another question clearly starts.
    normalized = re.sub(
        r"\?\s+(?="
        r"(?:self|what|why|how|when|where|who|which|"
        r"can|could|would|should|write|find|check|list|"
        r"describe|explain|difference|method|puzzle|tell|"
        r"solve|implement|name|features|compare|code|coding)"
        r"\b)",
        "? | ",
        normalized,
        flags=re.IGNORECASE,
    )

    # Semicolons are safe boundaries.
    normalized = re.sub(
        r"\s*;\s*",
        " | ",
        normalized,
    )

    parts = re.split(
        r"\s*\|\s*",
        normalized,
    )

    cleaned = []

    for part in parts:
        candidate = re.sub(
            r"^(?:l1|l2|code|coding|questions?|technical\s+interview)"
            r"\s*[:\-]?\s*",
            "",
            part,
            flags=re.IGNORECASE,
        )

        candidate = candidate.strip(
            " ,;:.-()[]{}"
        )

        if not candidate:
            continue

        candidate = re.sub(
            r"\?\s+(?=[a-z])",
            " ",
            candidate,
        )

        if not _is_fragment_question(candidate):
            cleaned.append(candidate)

    return cleaned


# =========================================================
# EXPLICIT FIELD EXTRACTION
# =========================================================

def extract_explicit_field_values(text: str, field_names):
    if not text:
        return []

    results = []

    field_pattern = "|".join(
        re.escape(field)
        for field in field_names
    )

    next_section_pattern = (
        r"(?:company|rounds?|stage|question|questions|"
        r"difficulty|feedback|role|package|eligibility|"
        r"code|dept|department|l1|l2)"
    )

    pattern = re.compile(
        rf"(?:^|\n|\s)"
        rf"(?:{field_pattern})"
        rf"\s*[:\-]\s*"
        rf"(.*?)"
        rf"(?="
        rf"\s+{next_section_pattern}\s*[:\-]"
        rf"|\n|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )

    for match in pattern.finditer(text):
        value = match.group(1).strip()

        if value:
            results.append(value)

    return results


# =========================================================
# QUESTION EXTRACTION
# =========================================================

def extract_questions(text: str):
    if not text:
        return []

    questions = []
    seen = set()

    def add_candidate(candidate):
        if not candidate:
            return

        candidate = str(candidate).strip()

        # Remove numbering.
        candidate = re.sub(
            r"^\s*\d+\s*[\.\):\-]\s*",
            "",
            candidate,
        )

        # Remove bullets.
        candidate = re.sub(
            r"^\s*[-*•]\s*",
            "",
            candidate,
        )

        candidate = candidate.strip()

        if not candidate:
            return

        lower = candidate.lower()

        # Ignore topic headings.
        if re.match(
            r"^(?:technical|coding|system design|aptitude|"
            r"communication|programming)\s+topics?\s*[:\-]",
            lower,
        ):
            return

        # Ignore known topic-list lines.
        topic_list_patterns = [
            r"^arrays,\s*linked lists,\s*trees,\s*algorithms$",
            r"^c\+\+,\s*data structures,\s*operating systems,\s*computer architecture$",
            r"^scalability,\s*apis,\s*database design$",
        ]

        for pattern in topic_list_patterns:
            if re.fullmatch(pattern, lower):
                return

        # Ignore field labels.
        if re.match(
            r"^(?:difficulty|batch|company|package|role|"
            r"eligibility|student feedback)\s*[:\-]",
            lower,
        ):
            return

        candidate = strip_field_prefixes(candidate)

        # Fix accidental question marks.
        candidate = re.sub(
            r"\?\s+(?=[a-z])",
            " ",
            candidate,
        )

        candidate = re.sub(
            r"\s+",
            " ",
            candidate,
        ).strip()

        if _is_fragment_question(candidate):
            return

        # A valid question should begin with a question-like
        # command/starter.
        question_starters = (
            r"^(?:what|why|how|which|when|where|who|can|could|"
            r"would|should|do|did|does|write|find|check|list|"
            r"describe|explain|name|difference|tell|solve|"
            r"implement|code|are|is|was|were)\b"
        )

        if not re.match(
            question_starters,
            candidate,
            re.IGNORECASE,
        ):
            return

        # Do not store round descriptions as questions.
        if any(
            phrase in lower
            for phrase in [
                "first round",
                "second round",
                "third round",
                "fourth round",
                "coding round",
                "aptitude round",
                "technical round",
                "hr round",
                "round was",
                "round had",
            ]
        ):
            return

        # Avoid storing strengths/weaknesses alone.
        if (
            "strengths" in lower
            or "weaknesses" in lower
        ):
            if "tell me about yourself" not in lower:
                return

        # Add question mark.
        candidate = candidate.rstrip(
            " .;:!?"
        ) + "?"

        # Normalize OOPS/OOP for duplicate detection.
        dedupe_key = re.sub(
            r"\boops\b",
            "oop",
            candidate.lower(),
        )

        dedupe_key = re.sub(
            r"\s+",
            " ",
            dedupe_key,
        ).strip()

        if dedupe_key not in seen:
            questions.append(candidate)
            seen.add(dedupe_key)

    # ---------------------------------------------------------
    # Process line by line.
    # ---------------------------------------------------------

    lines = text.splitlines()

    in_question_section = False
    in_topic_section = False

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        lower = line.lower()

        # -----------------------------------------------------
        # Topic section.
        # -----------------------------------------------------

        if re.match(
            r"^(?:technical|coding|system design|aptitude|"
            r"communication|programming)\s+topics?\s*[:\-]",
            lower,
        ):
            in_topic_section = True
            in_question_section = False
            continue

        # -----------------------------------------------------
        # Question section.
        # -----------------------------------------------------

        if re.match(
            r"^(?:sample\s+questions?|questions?|interview\s+questions?)"
            r"\s*[:\-]",
            lower,
        ):
            in_question_section = True
            in_topic_section = False

            value = re.sub(
                r"^(?:sample\s+questions?|questions?|interview\s+questions?)"
                r"\s*[:\-]\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()

            if value:
                for item in split_question_items(value):
                    add_candidate(item)

            continue

        # -----------------------------------------------------
        # Difficulty / other section means question section ends.
        # -----------------------------------------------------

        if re.match(
            r"^difficulty\s*[:\-]",
            lower,
        ):
            in_question_section = False
            in_topic_section = False
            continue

        if re.match(
            r"^(?:company|batch|package|role|eligibility|"
            r"recruitment|recruitment flow|round|rounds?)\s*[:\-]",
            lower,
        ):
            in_question_section = False
            in_topic_section = False
            continue

        # -----------------------------------------------------
        # Ignore topic content.
        # -----------------------------------------------------

        if in_topic_section:
            continue

        # -----------------------------------------------------
        # Process question-section content.
        # -----------------------------------------------------

        if in_question_section:
            for item in split_question_items(line):
                add_candidate(item)

            continue

        # -----------------------------------------------------
        # Standalone questions outside explicit section.
        # -----------------------------------------------------

        if re.match(
            r"^(?:what|why|how|which|when|where|who|can|could|"
            r"would|should|do|did|does|write|find|check|list|"
            r"describe|explain|name|difference|tell|solve|"
            r"implement|code|are|is|was|were)\b",
            lower,
        ):
            for item in split_question_items(line):
                add_candidate(item)

    # ---------------------------------------------------------
    # Common direct coding/interview questions.
    # ---------------------------------------------------------

    direct_commands = [
        "reverse a string",
        "find duplicate elements in an array",
        "find duplicate in array",
        "check anagram of two strings",
        "write code for prime numbers 1-n",
        "explain normalization in dbms",
        "difference between process and thread",
        "tell me about yourself",
        "why should we hire you",
        "are you willing to relocate",
        "what is the difference between process and thread",
        "longest substring without repeating characters",
        "second highest salary sql query",
        "what is oop",
        "what is polymorphism",
        "difference between abstract class and interface",
    ]

    lower_text = text.lower()

    for command in direct_commands:
        if command in lower_text:
            add_candidate(command)

    return questions


# =========================================================
# FEEDBACK
# =========================================================

def extract_feedback(text: str):
    if not text:
        return []

    feedback = []

    lines = text.splitlines()

    in_feedback_section = False

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        lower = line.lower()

        # -----------------------------------------------------
        # Student feedback section.
        # -----------------------------------------------------

        if re.match(
            r"^student\s+feedback\s*[:\-]",
            lower,
        ):
            in_feedback_section = True

            # Support:
            # Student feedback: The interviewer was friendly.
            value = re.sub(
                r"^student\s+feedback\s*[:\-]\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()

            if value:
                value = value.strip(" .;:!?")

                if value and value not in feedback:
                    feedback.append(value)

            continue

        # -----------------------------------------------------
        # Stop feedback when a new section starts.
        # -----------------------------------------------------

        if in_feedback_section and re.match(
            r"^(?:difficulty|company|batch|package|role|"
            r"eligibility|recruitment|round|rounds?|"
            r"technical topics?|coding topics?|"
            r"system design topics?|sample questions?|"
            r"questions?)\s*[:\-]",
            lower,
        ):
            in_feedback_section = False
            continue

        if not in_feedback_section:
            continue

        clean = line.strip(" .;:!?")

        if clean and clean not in feedback:
            feedback.append(clean)

    # ---------------------------------------------------------
    # Older feedback formats.
    # ---------------------------------------------------------

    if not feedback:
        markers = [
            "friendly",
            "resume based",
            "resume",
            "time consuming",
            "follow-up",
            "follow up",
            "no coding on paper",
            "no coding",
            "very friendly",
            "mostly resume",
            "only resume",
            "interviewer",
        ]

        sentences = re.split(
            r"(?<=\.)\s+|\n+",
            text,
        )

        for sentence in sentences:
            clean = sentence.strip()

            if not clean:
                continue

            lower = clean.lower()

            if re.match(
                r"^difficulty\s*[:\-]",
                lower,
            ):
                continue

            if re.match(
                r"^(?:company|role|package|eligibility|"
                r"batch|round|rounds?|topics?|technical topics?|"
                r"coding topics?|system design topics?)\s*[:\-]",
                lower,
            ):
                continue

            if not any(
                marker in lower
                for marker in markers
            ):
                continue

            if re.search(
                r"\b(?:what|why|how|difference between|explain|"
                r"find|reverse|write|tell me about yourself)\b",
                lower,
            ):
                continue

            clean = clean.strip(" .;:!?")

            if clean and clean not in feedback:
                feedback.append(clean)

    return feedback


# =========================================================
# MAIN NLP EXTRACTION
# =========================================================

def extract_information(text: str):
    """
    Main NLP extraction function.

    Returns the same structure expected by the
    existing storage/NLP pipeline.
    """

    company = extract_company_name(text)
    role = extract_role(text)
    rounds = extract_rounds(text)
    topics = extract_topics(text)
    difficulty = extract_difficulty(text)
    questions = extract_questions(text)
    feedback = extract_feedback(text)

    info = {
        "company": company,
        "minimum_cgpa": extract_cgpa(text),
        "maximum_backlogs": extract_backlogs(text),
        "rounds": rounds,
        "topics": topics,
        "difficulty": difficulty,
        "questions": questions,
        "feedback": feedback,
    }

    # Keep role available for callers that want it.
    if role:
        info["job_role"] = role

    return info
