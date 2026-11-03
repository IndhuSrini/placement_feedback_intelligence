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
    "programming",
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
    # Communication / Verbal
    "reading comprehension": "Reading Comprehension",
    "comprehension": "Reading Comprehension",
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "verbal ability": "Verbal Ability",
    "verbal": "Verbal Ability",
    "sentence correction": "Sentence Correction",
    "synonyms": "Synonyms",
    "antonyms": "Antonyms",

    # Aptitude
    "quantitative aptitude": "Quantitative Aptitude",
    "quantitative": "Quantitative Aptitude",
    "percentages": "Percentages",
    "percentage": "Percentages",
    "profit and loss": "Profit and Loss",
    "ratio": "Ratio",
    "ratios": "Ratio",
    "ratio and proportion": "Ratio",
    "probability": "Probability",
    "time and work": "Time and Work",
    "time speed distance": "Time Speed Distance",
    "logical reasoning": "Logical Reasoning",
    "reasoning": "Logical Reasoning",
    "data interpretation": "Data Interpretation",
    "number series": "Number Series",
    "blood relations": "Blood Relations",
    "seating arrangement": "Seating Arrangement",
    "coding and decoding": "Coding and Decoding",
    "syllogisms": "Syllogisms",
    "syllogism": "Syllogisms",
    "permutations and combinations": "Permutations and Combinations",
    "simple and compound interest": "Simple and Compound Interest",
    "averages": "Averages",
    "clocks and calendars": "Clocks and Calendars",

    # Coding / DSA
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
    "binary tree": "Tree",
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
    "data structures": "Data Structures",

    # Core Technical
    "oops": "OOP",
    "oop": "OOP",
    "object oriented programming": "OOP",
    "polymorphism": "Polymorphism",
    "inheritance": "Inheritance",
    "encapsulation": "Encapsulation",
    "abstraction": "Abstraction",
    "method overloading": "OOP",
    "method overriding": "OOP",
    "abstract class": "OOP",
    "interface": "OOP",
    "exception handling": "Exception Handling",
    "collections": "Collections",
    "dbms": "DBMS",
    "database": "DBMS",
    "normalization": "DBMS",
    "sql": "SQL",
    "joins": "Joins",
    "join": "Joins",
    "operating system": "Operating System",
    "operating systems": "Operating System",
    "thread": "Thread",
    "deadlock": "Deadlock",
    "computer networks": "Computer Networks",
    "computer architecture": "Computer Architecture",
    "tcp/ip": "TCP/IP",
    "tcp": "TCP/IP",
    "http": "HTTP",
    "rest api": "REST API",
    "apis": "REST API",
    "api": "REST API",
    "microservices": "Microservices",
    "scalability": "System Design",
    "system design": "System Design",
    "java": "Java",
    "python": "Python",
    "c++": "C++",
    "c": "C",
    "jdk": "JDK",
    "jre": "JRE",
    "jvm": "JVM",
    "jdk, jre and jvm": "JDK, JRE and JVM",
    "jre and jvm": "JDK, JRE and JVM",

    # HR
    "strengths": "Strengths",
    "weaknesses": "Weaknesses",
    "introduction": "Introduction",
    "tell me about yourself": "Tell Me About Yourself",
    "about yourself": "Tell Me About Yourself",
    "relocation": "Relocation",
    "salary": "Salary",
    "career goals": "Career Goals",
    "hobbies": "Hobbies",
}


QUESTION_STARTERS = (
    r"^(?:(?:you\s+have)|asked|puzzle|self|what|why|how|which|when|where|who|"
    r"can|could|would|should|do|did|does|write|find|check|list|describe|explain|"
    r"name|difference|tell|solve|implement|code|reverse|longest|compare|are|is|was|were|"
    r"swap|print|sort|count|convert|construct|merge|calculate|determine|generate|"
    r"traverse|search|insert|delete|rotate|detect|remove)\b"
)


INCOMPLETE_ENDINGS = {
    "to", "the", "a", "an", "of", "for", "with", "between", "when", "where",
    "which", "that", "and", "or", "whether", "if", "from", "in", "on", "about",
    "into", "as", "than", "by", "your", "their", "our", "my",
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
    if lowered in {"included", "topics", "topic", "round", "questions", "question"}:
        return None

    if lowered in TOPIC_ALIASES:
        return TOPIC_ALIASES[lowered]

    for alias, canonical in TOPIC_ALIASES.items():
        alias_pattern = (
            r"(?<![a-z0-9])"
            + re.escape(alias).replace(r"\ ", r"\s+")
            + r"(?![a-z0-9])"
        )
        if re.search(alias_pattern, lowered):
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
    if "very hard" in lowered or "hard" in lowered or "difficult" in lowered:
        return "Hard"
    return None


def normalize_company_name(name: str):
    if not name:
        return None

    cleaned = str(name).strip()
    cleaned = re.sub(
        r"^company\s*[:\-–—―−]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = cleaned.strip(" .;:-–—―−")
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
            elif any(c.isupper() for c in part[1:]):
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
            r"code|dept|department|l1|l2)\s*[:\-–—―−]?\s*",
            text,
            flags=re.IGNORECASE,
        )
        if not match:
            return text.strip()
        text = text[match.end():].strip()


# =========================================================
# COMPANY & ROLE
# =========================================================

def extract_company_name(text: str):
    if not text:
        return None

    patterns = [
        r"(?:^|\n)\s*\d+\.\s*company(?:[ \t]+name)?"
        r"(?:[ \t]*[:\-–—―−][ \t]*|[ \t]+)([^\n]+)",
        r"(?:^|\n)\s*company(?:[ \t]+name)?"
        r"(?:[ \t]*[:\-–—―−][ \t]*|[ \t]+)([^\n]+)",
        r"\bcompany(?:[ \t]+name)?"
        r"(?:[ \t]*[:\-–—―−][ \t]*|[ \t]+)([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        candidate = match.group(1).strip()
        boundary_pattern = (
            r"\s+(?:"
            + "|".join(re.escape(w) for w in COMPANY_BOUNDARY_WORDS)
            + r")\s*[:\-–—―−]?"
        )
        candidate = re.split(
            boundary_pattern,
            candidate,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        candidate = candidate.strip(" .;:-–—―−")
        if candidate:
            return normalize_company_name(candidate)

    return None


def extract_role(text: str):
    if not text:
        return None

    patterns = [
        r"(?:^|\n)\s*\d+\.\s*(?:job\s+)?role\s*[:\-–—―−]\s*([^\n]+)",
        r"(?:^|\n)\s*(?:job\s+)?role\s*[:\-–—―−]\s*([^\n]+)",
        r"\b(?:job\s+)?role\s*[:\-–—―−]\s*([^\n]+)",
        r"\b(?:hiring|drive)\s+for\s+([A-Za-z][A-Za-z0-9 /&.-]+?)(?=\s+(?:in|for)\s+(?:the\s+)?20\d{2}|\s+batch\b|[.,\n]|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue

        value = match.group(1).strip()
        value = re.sub(r"^(?:hiring|drive)\s+for\s+", "", value, flags=re.IGNORECASE)
        value = re.split(
            r"\s+(?=(?:company|batch|package|eligibility|round|rounds|"
            r"difficulty|topic|topics|question|questions|recruitment|"
            r"student\s+feedback)\s*[:\-–—―−])",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        value = re.split(
            r"\s+(?:(?:in|for)\s+)?(?:the\s+)?20\d{2}\s*[-/]\s*(?:20)?\d{2}\s+batch\b"
            r"|\s+in\s+(?:the\s+)?20\d{2}\b",
            value,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        value = value.strip(" .;:-–—―−")
        if value:
            return value

    return None


# =========================================================
# ROUND INFERENCE & EXTRACTION
# =========================================================

def infer_round_type(text: str):
    lower = text.lower().strip()

    if "communication" in lower:
        return "Communication"

    if (
        "aptitude" in lower
        or "quantitative" in lower
        or "logical" in lower
        or "reasoning" in lower
        or "verbal" in lower
    ):
        return "Aptitude"

    if (
        "coding" in lower
        or "programming" in lower
        or "algorithm" in lower
    ):
        return "Coding"

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
        or "human resources" in lower
    ):
        return "HR"

    if "group discussion" in lower or re.search(r"\bgd\b", lower):
        return "Group Discussion"

    if "written test" in lower or lower == "written":
        return "Written Test"

    if "presentation" in lower:
        return "Presentation"

    if "case study" in lower:
        return "Case Study"

    if "behavioral" in lower:
        return "Behavioral"

    if "assessment" in lower or "online assessment" in lower or "online test" in lower:
        return "Aptitude"

    if "interview" in lower:
        return "Interview"

    return "Unknown"


ROUND_CATEGORY_MAP = {
    "Communication": "Communication",
    "Aptitude": "Aptitude",
    "Coding": "Coding",
    "Technical": "Technical",
    "System Design": "Technical",
    "HR": "HR",
    "Managerial": "HR",
    "Behavioral": "HR",
    "Group Discussion": "Communication",
    "Written Test": "Aptitude",
    "Interview": "Technical",
}


def _parse_number_word(value: str):
    if not value:
        return None
    mapping = {
        "first": 1, "1st": 1, "1": 1,
        "second": 2, "2nd": 2, "2": 2,
        "third": 3, "3rd": 3, "3": 3,
        "fourth": 4, "4th": 4, "4": 4,
        "fifth": 5, "5th": 5, "5": 5,
        "sixth": 6, "6th": 6, "6": 6,
        "seventh": 7, "7th": 7, "7": 7,
        "eighth": 8, "8th": 8, "8": 8,
        "ninth": 9, "9th": 9, "9": 9,
        "tenth": 10, "10th": 10, "10": 10,
    }
    return mapping.get(str(value).lower().strip())


def extract_rounds(text: str):
    if not text:
        return []

    rounds = []
    seen = set()

    def add_round(round_number, round_type, description):
        if not round_type or round_type == "Unknown":
            return
        key = (round_number, round_type.lower())
        if key in seen:
            return
        rounds.append({
            "round_number": round_number,
            "round_type": round_type,
            "description": description.strip(" .;:-–—―−"),
        })
        seen.add(key)

    numbered_patterns = [
        r"(?:^|\n)\s*round\s*(?:no\.?|number)?\s*(\d+)\s*[:\-–—―−.]?\s*([^\n]+)",
        r"(?:^|\n)\s*(\d+)(?:st|nd|rd|th)\s+round\s*[:\-–—―−.]?\s*([^\n]+)",
        r"\bround\s*(?:no\.?|number)?\s*(\d+)\s*[:\-–—―−.]?\s*([A-Za-z][A-Za-z0-9 ,/&()-]*)",
        r"\b(\d+)(?:st|nd|rd|th)\s+round\s*[:\-–—―−.]?\s*([A-Za-z][A-Za-z0-9 ,/&()-]*)",
        r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+round\s*[:\-–—―−.]?\s*([A-Za-z][A-Za-z0-9 ,/&()-]*?)(?=\s+(?:and\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+round\b|[.,;!?]|\n|$)",
    ]

    for pattern in numbered_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            round_number = _parse_number_word(match.group(1))
            label = match.group(2).strip()
            label = re.split(
                r"\s+(?:and\s+(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b|was|is|are|had|with|question|questions|difficulty|feedback|role|eligibility|topic|topics)\b",
                label,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip(" .;:-–—―−")

            round_type = infer_round_type(label)
            if round_type != "Unknown":
                add_round(round_number, round_type, label)

    # Round Flow
    flow_patterns = [
        r"\bround\s*flow\s*[:\-–—―−][ \t]*([^\n]+)",
        r"\brounds?\s*[:\-–—―−][ \t]*([^\n]+)",
        r"\binterview\s*flow\s*[:\-–—―−][ \t]*([^\n]+)",
        r"\brecruitment\s+flow\s*[:\-–—―−][ \t]*([^\n]+)",
    ]

    for pattern in flow_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            continue
        value = re.split(
            r"\s+(?:difficulty|topic|topics|question|questions|eligibility|package|recruitment)\s*[:\-–—―−]",
            match.group(1),
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        parts = re.split(r",|->|>|/|\s+then\s+|\s+and\s+", value, flags=re.IGNORECASE)
        next_number = 1 if len(parts) > 1 else None
        for part in parts:
            label = part.strip(" .;:-–—―−")
            if not label:
                continue
            round_type = infer_round_type(label)
            if round_type != "Unknown":
                add_round(next_number, round_type, label)
                if next_number is not None:
                    next_number += 1

    # Generic Stage Mentions
    stage_patterns = [
        ("Aptitude", r"\baptitude\s+(?:round|test|assessment)\b"),
        ("Coding", r"\bcoding\s+(?:round|interview|test)\b"),
        ("Technical", r"\btechnical\s+interview\b"),
        ("System Design", r"\bsystem\s+design\s+(?:round|interview|stage)\b"),
        ("HR", r"\bhr\s+(?:round|interview|asked)\b"),
        ("Communication", r"\bcommunication\s+(?:round|interview|test|stage)\b"),
        ("Managerial", r"\bmanagerial\s+interview\b"),
        ("Group Discussion", r"\bgroup\s+discussion\b"),
        ("Written Test", r"\bwritten\s+test\b"),
    ]

    for round_type, pattern in stage_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            already_present = any(
                item["round_type"].lower() == round_type.lower()
                for item in rounds
            )
            if not already_present:
                add_round(None, round_type, round_type)

    rounds.sort(
        key=lambda item: (
            item["round_number"] is None,
            item["round_number"] if item["round_number"] is not None else 999,
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
        match = re.search(pattern, text, re.IGNORECASE)
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
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))

    if re.search(r"no\s+(?:active\s+)?backlogs?", text, re.IGNORECASE):
        return 0
    if re.search(r"no\s+standing\s+arrears", text, re.IGNORECASE):
        return 0
    return None


def extract_batch(text: str):
    if not text:
        return None
    patterns = [
        r"\bbatch(?:\s+of)?\s*[:\-–—―−]?\s*(20\d{2}\s*(?:-|to|/|–|—)\s*(?:20)?\d{2})\b",
        r"\b(20\d{2}\s*(?:-|to|/|–|—)\s*(?:20)?\d{2})\s+batch\b",
        r"\bbatch(?:\s+of)?\s*[:\-–—―−]?\s*(20\d{2})\b",
        r"\b(20\d{2})\s+batch\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = re.sub(r"\s+", "", match.group(1))
            return re.sub(r"[–—to/]", "-", raw)
    return None


def extract_year(text: str):
    if not text:
        return None
    match = re.search(
        r"\b(?:recruitment\s+date|drive\s+date|hiring\s+year|year)\s*[:\-–—―−]?\s*"
        r"[^.\n]*?\b(20\d{2})\b",
        text,
        re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


def extract_package(text: str):
    if not text:
        return None
    match = re.search(
        r"\b(?:package|ctc|salary)\s*[:\-–—―−]?\s*(?:₹|rs\.?\s*)?"
        r"(\d+(?:\.\d+)?)\s*(lpa|lakhs?|lacs?)(?:\s+per\s+annum)?\b",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return f"{match.group(1)} LPA"


def _eligibility_section(text: str):
    match = re.search(
        r"\b(?:eligibility\s+criteria|eligibility)\s*[:\-–—―−]\s*(.+)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    value = re.split(
        r"\s+(?=(?:company|role|job\s+role|batch|package|round|rounds|"
        r"recruitment(?:\s+flow)?|difficulty|questions?|topics?|"
        r"student\s+feedback|feedback)\s*[:\-–—―−])",
        match.group(1),
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return value.strip(" \t.;:-–—―−") or None


def extract_branch_eligibility(text: str):
    if not text:
        return None
    match = re.search(
        r"\b(?:eligible\s+branches?|branch\s+eligibility|branches?)\s*[:\-–—―−]\s*"
        r"([^\n.;]+)",
        text,
        re.IGNORECASE,
    )
    return match.group(1).strip(" \t,.;:-–—―−") if match else None


def extract_other_eligibility(text: str):
    value = _eligibility_section(text)
    if not value:
        return None
    value = re.sub(r"\b(?:minimum\s+)?\d+(?:\.\d+)?\s*(?:cgpa|gpa)\b", " ", value, flags=re.IGNORECASE)
    value = re.sub(
        r"\bno\s+(?:active\s+)?(?:standing\s+)?backlogs?\b"
        r"|\b(?:\d+|zero)\s+(?:active\s+)?backlogs?\b",
        " ",
        value,
        flags=re.IGNORECASE,
    )
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"^(?:and|or)\s+", "", value, flags=re.IGNORECASE)
    value = value.strip(" ,.;:-–—―−")
    return value or None


# =========================================================
# TOPICS & PREPARATION DETAILS
# =========================================================

def determine_topic_category(topic_name: str, fallback_round_category: str = None) -> str:
    normalized = str(topic_name).strip().lower()

    comm_keywords = [
        "reading comprehension", "grammar", "vocabulary", "verbal",
        "sentence correction", "synonym", "antonym", "communication",
    ]
    apt_keywords = [
        "aptitude", "percentage", "ratio", "profit and loss", "logical",
        "quantitative", "reasoning", "time and work", "time speed",
        "probability", "data interpretation", "number series",
        "blood relation", "seating arrangement", "syllogism",
        "interest", "average", "clock", "calendar",
    ]
    coding_keywords = [
        "array", "string", "linked list", "stack", "queue", "tree", "graph",
        "recursion", "dynamic programming", "sorting", "searching", "hashing",
        "binary search", "greedy", "data structure", "algorithm",
        "leetcode", "programming", "pointer", "heap",
    ]
    tech_keywords = [
        "dbms", "sql", "join", "oop", "operating system", "thread",
        "deadlock", "computer network", "tcp", "http", "api", "java",
        "python", "c++", "c#", "rest", "microservice", "system design",
        "exception", "inheritance", "polymorphism", "encapsulation",
        "abstraction", "collection", "jdk", "jre", "jvm",
    ]
    hr_keywords = [
        "strength", "weakness", "introduction", "yourself", "relocation",
        "salary", "career goal", "hobby", "hobbies", "hr",
    ]

    if any(kw in normalized for kw in comm_keywords):
        return "Communication"
    if any(kw in normalized for kw in apt_keywords):
        return "Aptitude"
    if any(kw in normalized for kw in coding_keywords):
        return "Coding"
    if any(kw in normalized for kw in tech_keywords):
        return "Technical"
    if any(kw in normalized for kw in hr_keywords):
        return "HR"

    if fallback_round_category:
        return fallback_round_category
    return "Other"


def extract_topics(text: str):
    if not text:
        return []

    lower_text = text.lower()
    found_topics = []

    def add_topic(topic):
        if topic and topic not in found_topics and topic != "Included":
            found_topics.append(topic)

    # OS Context check: only add Operating System / Process / Thread if genuinely OS
    has_os = bool(re.search(r"\boperating systems?\b", lower_text))
    has_thread = bool(re.search(r"\bthread\b", lower_text))
    has_proc = bool(re.search(r"\bprocess\b", lower_text))
    has_deadlock = bool(re.search(r"\bdeadlock\b", lower_text))

    if has_os:
        add_topic("Operating System")
    if (has_proc and has_thread and (has_os or re.search(r"\bos\b", lower_text))) or (has_os and has_proc):
        # Exclude if process is solely part of recruitment process
        cleaned_proc = re.sub(
            r"\b(?:recruitment|selection|interview|hiring|application)\s+process\b",
            "",
            lower_text,
        )
        if re.search(r"\bprocess(?:es)?\b", cleaned_proc):
            add_topic("Process")
            add_topic("Operating System")
    if has_thread:
        add_topic("Thread")
    if has_deadlock:
        add_topic("Deadlock")

    if "longest substring" in lower_text:
        add_topic("Strings")
        add_topic("Algorithms")

    if "second highest salary" in lower_text or "highest salary" in lower_text:
        add_topic("SQL")
        add_topic("DBMS")

    if (
        "abstract class" in lower_text
        or "interface" in lower_text
        or re.search(r"\boops?\b", lower_text)
    ):
        add_topic("OOP")

    if "rest api" in lower_text:
        add_topic("REST API")

    if "microservices" in lower_text:
        add_topic("Microservices")

    for alias, canonical in TOPIC_ALIASES.items():
        if alias in {"operating system", "operating systems", "os", "process", "thread"}:
            continue
        boundary_pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
        if re.search(boundary_pattern, lower_text):
            add_topic(canonical)

    return found_topics


# =========================================================
# SECTION-AWARE BLOCK PARSER
# =========================================================

def _split_into_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    current_block = {
        "type": "preamble",
        "round_number": None,
        "round_type": None,
        "category": None,
        "label": "",
        "lines": [],
    }

    round_header_re = re.compile(
        r"^(?:round\s*(?:no\.?|number)?\s*(\d+)?|(\d+)(?:st|nd|rd|th)\s+round)\s*[:\-–—―−.]?\s*(.+)$",
        re.IGNORECASE,
    )
    stage_header_re = re.compile(
        r"^(?:(?:technical|hr|managerial)\s+interview|coding\s+(?:assessment|round)|"
        r"aptitude\s+(?:assessment|round|test)|communication\s+(?:assessment|round)|"
        r"group\s+discussion|online\s+assessment)\b(?:\s*[:\-–—―−.]\s*(.*))?$",
        re.IGNORECASE,
    )
    global_section_re = re.compile(
        r"^(?:overall\s+difficulty|student\s+feedback|feedback)\s*[:\-–—―−]",
        re.IGNORECASE,
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if global_section_re.match(stripped):
            blocks.append(current_block)
            current_block = {
                "type": "global",
                "round_number": None,
                "round_type": None,
                "category": None,
                "label": stripped,
                "lines": [stripped],
            }
            continue

        m_round = round_header_re.match(stripped)
        if m_round:
            blocks.append(current_block)
            num_str = m_round.group(1) or m_round.group(2)
            number = int(num_str) if num_str else None
            label = m_round.group(3).strip()
            round_type = infer_round_type(label)
            category = ROUND_CATEGORY_MAP.get(round_type, "Technical")
            current_block = {
                "type": "round",
                "round_number": number,
                "round_type": round_type,
                "category": category,
                "label": label,
                "lines": [],
            }
            continue

        m_stage = stage_header_re.match(stripped)
        if m_stage and not stripped.lower().endswith("?"):
            blocks.append(current_block)
            label = stripped
            round_type = infer_round_type(label)
            category = ROUND_CATEGORY_MAP.get(round_type, "Technical")
            current_block = {
                "type": "round",
                "round_number": None,
                "round_type": round_type,
                "category": category,
                "label": label,
                "lines": [],
            }
            continue

        current_block["lines"].append(stripped)

    blocks.append(current_block)
    return blocks


def extract_preparation_topic_details(text: str, rounds: list):
    if not text:
        return []

    blocks = _split_into_blocks(text)
    details = []
    seen = set()

    rounds_by_type = {r["round_type"].lower(): r for r in rounds if r.get("round_type")}

    topic_section_re = re.compile(
        r"^(?:(?P<section>aptitude|coding|technical|system\s+design|communication|programming)\s+)?topics?\s*(?:included|are|were)?\s*[:\-–—―−.]\s*(?P<value>.*)$",
        re.IGNORECASE,
    )
    bullet_re = re.compile(r"^[•●▪▫✦★■◆\-*]\s*(.+)$")

    for block in blocks:
        block_round_num = block.get("round_number")
        block_round_type = block.get("round_type")
        block_category = block.get("category")

        if block_round_num is None and block_round_type:
            matched_r = rounds_by_type.get(block_round_type.lower())
            if matched_r:
                block_round_num = matched_r.get("round_number")

        in_topic_mode = False
        active_category = block_category or "Technical"
        explicit_technical_section = False

        for line in block.get("lines", []):
            m_sec = topic_section_re.match(line)
            if m_sec:
                in_topic_mode = True
                sec_word = m_sec.group("section")
                if sec_word:
                    cat = sec_word.strip().title()
                    if cat.lower() == "programming":
                        cat = "Coding"
                    active_category = cat
                    if cat.lower() == "technical":
                        explicit_technical_section = True
                else:
                    active_category = block_category or "Technical"

                val = m_sec.group("value").strip()
                if val:
                    items = re.split(r"[,;]|\s+and\s+", val)
                    for item in items:
                        t_name = normalize_topic_name(item)
                        if t_name and t_name != "Included":
                            cat = determine_topic_category(t_name, active_category)
                            round_num_to_assign = None if explicit_technical_section else block_round_num
                            key = (t_name.casefold(), cat.casefold())
                            if key not in seen:
                                details.append({
                                    "topic": t_name,
                                    "category": cat,
                                    "round_number": round_num_to_assign,
                                })
                                seen.add(key)
                continue

            if re.match(
                r"^(?:sample\s+questions?|questions?|sample\s+problems?|problems?|"
                r"questions\s+discussed|difficulty|feedback|student\s+feedback|eligibility)\b",
                line,
                re.IGNORECASE,
            ):
                in_topic_mode = False
                continue

            if in_topic_mode:
                m_bullet = bullet_re.match(line)
                candidate_text = m_bullet.group(1).strip() if m_bullet else line
                if candidate_text.endswith("?") or re.match(QUESTION_STARTERS, candidate_text, re.IGNORECASE):
                    in_topic_mode = False
                    continue

                items = re.split(r"[,;]", candidate_text)
                for item in items:
                    t_name = normalize_topic_name(item)
                    if t_name and t_name != "Included":
                        cat = determine_topic_category(t_name, active_category)
                        round_num_to_assign = None if explicit_technical_section else block_round_num
                        key = (t_name.casefold(), cat.casefold())
                        if key not in seen:
                            details.append({
                                "topic": t_name,
                                "category": cat,
                                "round_number": round_num_to_assign,
                            })
                            seen.add(key)

    return details


# =========================================================
# QUESTION EXTRACTION & NORMALIZATION
# =========================================================

def _is_fragment_question(candidate: str) -> bool:
    if not candidate:
        return True

    text = str(candidate).strip().strip(" .;:!?(),[]{}\\\"'")
    if not text:
        return True

    lower = text.lower()
    if re.fullmatch(
        r"(?:s|l1|l2|what|why|how|explain|write|do|did|"
        r"does|can|would|should|which|who|when|where|self|"
        r"code|coding|find|check|list|describe|name|difference|"
        r"method|puzzle|feature|features|how to)",
        lower,
    ):
        return True

    if re.fullmatch(r"(?:what\s+is\s+(?:the|a|an))", lower):
        return True
    if re.fullmatch(r"(?:difference\s+between)", lower):
        return True

    words = lower.split()
    if len(words) < 2:
        return True
    if words[-1] in INCOMPLETE_ENDINGS:
        return True

    incomplete_patterns = [
        r"^write\s+(?:a|an|the)?\s*(?:program|code|query)?\s*$",
        r"^explain\s+(?:the|a|an|your)\s*$",
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
        if re.fullmatch(pattern, lower):
            return True

    return False


def normalize_question_text(question: str):
    if not question:
        return ""

    text = str(question).strip()
    text = re.sub(r"^\s*\d+\s*[\.\):\-]\s*", "", text)
    text = re.sub(r"^\s*[-*•●▪▫✦★■◆]\s*", "", text)
    text = re.sub(
        r"^(?:technical\s+interview|interview|hr|they|he|she|interviewer|candidate)\s+asked\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^(?:asked\s+to|asked\s+about|question\s+is|question\s+was)\s+",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^(?:coding|programming|technical|aptitude|hr)\s+(?:question|round)\s*[:\-–—―−]?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^(?:l1|l2|code|coding|questions?|technical\s+interview)\s*[:\-–—―−]?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\?\s+(?=[a-z])", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" .;:!?(),[]{}\\\"'")

    if not text or _is_fragment_question(text):
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
    normalized = re.sub(
        r"\b(?:l1\s*,?\s*l2|l2\s*,?\s*l1)\s*questions?\s*[:\-–—―−]?\s*",
        " ",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"\b(?:technical\s+interview\s+)?questions?\s*[:\-–—―−]?\s*",
        " ",
        normalized,
        flags=re.IGNORECASE,
    )

    # Newlines, pipes, semicolons
    normalized = re.sub(r"\s*\n+\s*", " | ", normalized)
    normalized = re.sub(r"\s*\|\s*", " | ", normalized)
    normalized = re.sub(r"\s*;\s*", " | ", normalized)

    # Numbered list markers
    normalized = re.sub(r"(?<=[a-zA-Z0-9?])\s+(?=\d+\.\s+[A-Za-z])", " | ", normalized)

    # Unpunctuated adjacent questions
    normalized = re.sub(
        r"(?<=[a-z0-9])\s+(?=(?:Self|What|Why|How|When|Where|Who|"
        r"Which|Can|Could|Would|Should|Write|Find|Check|List|"
        r"Describe|Explain|Difference|Method|Puzzle|Tell|Solve|"
        r"Implement|Name|Features|Compare|Code|Coding|Reverse|"
        r"Longest|Swap|Print|Sort)\b)",
        " | ",
        normalized,
    )

    # Split after ? only when followed by a fresh question starter
    normalized = re.sub(
        r"\?\s*(?=(?:self|what|why|how|when|where|who|which|can|could|would|should|"
        r"write|find|check|list|describe|explain|difference|method|puzzle|tell|"
        r"solve|implement|name|features|compare|code|coding|swap|print|sort|reverse)\b)",
        "? | ",
        normalized,
        flags=re.IGNORECASE,
    )

    # Split separate sentences only if NOT a compound question
    normalized = re.sub(
        r"(?<=[.!])\s*(?=(?:self|what|why|how|when|where|who|which|can|could|would|"
        r"should|write|find|check|list|describe|explain|difference|method|puzzle|"
        r"tell|solve|implement|name|features|compare|code|coding|swap|print|sort|reverse)\b)",
        " | ",
        normalized,
        flags=re.IGNORECASE,
    )

    # Separate distinct imperative clauses joined by "and"
    if not re.search(r"\b(?:what|why|how|which)\b[^.?!]*\band\s+(?:why|how|when|what|which)\b", normalized, re.IGNORECASE):
        normalized = re.sub(
            r"\s+\band\s+(?=(?:find\s+duplicate|reverse\s+a|check\s+whether|check\s+if|write\s+(?:a\s+)?(?:program|code)|sort\s+an?\b|swap\s+two\b))",
            " | ",
            normalized,
            flags=re.IGNORECASE,
        )

    parts = re.split(r"\s*\|\s*", normalized)
    cleaned = []
    for part in parts:
        candidate = re.sub(
            r"^(?:l1|l2|code|coding|questions?|technical\s+interview)\s*[:\-–—―−]?\s*",
            "",
            part,
            flags=re.IGNORECASE,
        ).strip(" ,;:.-()[]{}")
        if not candidate:
            continue
        candidate = re.sub(r"\?\s+(?=[a-z])", " ", candidate)
        if not _is_fragment_question(candidate):
            cleaned.append(candidate)

    return cleaned


def extract_questions(text: str):
    if not text:
        return []

    questions = []
    seen = set()

    def add_candidate(candidate):
        if not candidate:
            return
        c = str(candidate).strip()
        c = re.sub(r"^\s*\d+\s*[\.\):\-]\s*", "", c)
        c = re.sub(r"^\s*[-*•●▪▫✦★■◆]\s*", "", c)
        c = re.sub(r"^(?:asked\s+(?:to|about)\s+|puzzle\s*[:\-–—―−]?\s*)", "", c, flags=re.IGNORECASE)
        c = c.strip()
        if not c:
            return

        lower = c.lower()
        if re.match(
            r"^(?:technical|coding|programming|system design|aptitude|communication)\s+topics?\s*[:\-–—―−]",
            lower,
        ):
            return
        if re.match(
            r"^(?:difficulty|batch|company|package|role|eligibility|student feedback)\s*[:\-–—―−]",
            lower,
        ):
            return

        c = strip_field_prefixes(c)
        c = re.sub(r"\?\s+(?=[a-z])", " ", c)
        c = re.sub(r"\s+", " ", c).strip()

        if _is_fragment_question(c):
            return

        if not re.match(QUESTION_STARTERS, c, re.IGNORECASE):
            return

        if any(
            phrase in lower
            for phrase in [
                "first round", "second round", "third round", "fourth round",
                "coding round", "aptitude round", "technical round", "hr round",
                "round was", "round had",
            ]
        ):
            return

        if ("strengths" in lower or "weaknesses" in lower) and "tell me about yourself" not in lower:
            return

        c = c.rstrip(" .;:!?") + "?"
        dedupe_key = re.sub(r"\boops\b", "oop", c.lower())
        dedupe_key = re.sub(r"\s+", " ", dedupe_key).strip()

        if dedupe_key not in seen:
            questions.append(c)
            seen.add(dedupe_key)

    lines = text.splitlines()
    in_question_section = False
    in_topic_section = False

    question_section_re = re.compile(
        r"^(?:(?:aptitude|coding|programming|technical|hr|system design|"
        r"communication)(?:\s+(?:interview|round|assessment|test|stage))?\s+questions?|"
        r"sample\s+questions?|"
        r"questions?(?:\s+(?:discussed|asked|included))?|"
        r"interview\s+questions?|"
        r"programming\s+problems?|"
        r"l1\s*,?\s*l2\s+questions?|l2\s*,?\s*l1\s+questions?)"
        r"\s*(?:included|were|are)?\s*[:\-–—―−]",
        re.IGNORECASE,
    )
    topic_section_re = re.compile(
        r"^(?:(?:technical|coding|programming|system design|aptitude|communication)\s+)?topics?\s*(?:included|are|were)?\s*[:\-–—―−]",
        re.IGNORECASE,
    )
    stop_section_re = re.compile(
        r"^(?:difficulty|company|batch|package|role|eligibility|"
        r"recruitment|recruitment flow|round|rounds?)\s*[:\-–—―−]",
        re.IGNORECASE,
    )

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if topic_section_re.match(line):
            in_topic_section = True
            in_question_section = False
            continue

        if question_section_re.match(line):
            in_question_section = True
            in_topic_section = False
            val = question_section_re.sub("", line).strip()
            if val:
                for item in split_question_items(val):
                    add_candidate(item)
            continue

        if stop_section_re.match(line):
            in_question_section = False
            in_topic_section = False
            continue

        if in_topic_section:
            continue

        if in_question_section:
            for item in split_question_items(line):
                add_candidate(item)
            continue

        # Standalone question check
        cleaned_line = re.sub(r"^\s*\d+\s*[\.\):\-]\s*", "", line).strip()
        cleaned_line = re.sub(r"^\s*[-*•●▪▫✦★■◆]\s*", "", cleaned_line).strip()
        if re.match(QUESTION_STARTERS, cleaned_line, re.IGNORECASE):
            for item in split_question_items(line):
                add_candidate(item)

    # Direct common commands
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


def extract_question_details(
    questions: list,
    topic_details: list,
    text: str = "",
    rounds: list = None,
):
    if not questions:
        return []

    rounds = rounds or []
    blocks = _split_into_blocks(text) if text else []

    block_map = {}
    for block in blocks:
        block_lines = block.get("lines", [])
        if not block_lines:
            continue
        block_text = "\n".join(block_lines)
        block_q = extract_questions(block_text)
        for q in block_q:
            k = re.sub(r"[^a-z0-9]", "", q.lower())
            if k not in block_map:
                block_map[k] = block

    rounds_by_type = {r["round_type"].lower(): r for r in rounds if r.get("round_type")}

    details = []
    for question in questions:
        q_key = re.sub(r"[^a-z0-9]", "", question.lower())
        block = block_map.get(q_key)

        # Fallback block matching: check if question words appear in any block's lines
        if not block:
            for b in blocks:
                b_text = " ".join(b.get("lines", [])).lower()
                clean_q = re.sub(r"[^a-z0-9\s]", "", question.lower()).strip()
                if clean_q and clean_q in re.sub(r"[^a-z0-9\s]", "", b_text):
                    block = b
                    break

        block = block or {}
        matched_round_num = block.get("round_number")
        matched_round_type = block.get("round_type")
        block_cat = block.get("category")

        if matched_round_num is None and matched_round_type:
            r_obj = rounds_by_type.get(matched_round_type.lower())
            if r_obj:
                matched_round_num = r_obj.get("round_number")

        # Determine topic
        matched_topic = None
        q_lower = question.lower()
        for td in topic_details:
            t_name = td.get("topic", "")
            if t_name and re.search(rf"\b{re.escape(t_name.lower())}\b", q_lower):
                matched_topic = t_name
                if not block_cat:
                    block_cat = td.get("category")
                if matched_round_num is None:
                    matched_round_num = td.get("round_number")
                break

        category = block_cat
        if not category:
            if any(w in q_lower for w in ["relocate", "hire you", "about yourself", "weakness", "strength", "hobbies"]):
                category = "HR"
            elif any(w in q_lower for w in ["swap", "print", "fibonacci", "reverse", "palindrome", "array", "linked list", "tree"]):
                category = "Coding"
            elif any(w in q_lower for w in ["dbms", "sql", "oop", "polymorphism", "java", "inheritance", "class"]):
                category = "Technical"
            elif any(w in q_lower for w in ["percentage", "ratio", "profit", "loss", "speed", "distance"]):
                category = "Aptitude"
            elif any(w in q_lower for w in ["grammar", "vocabulary", "comprehension"]):
                category = "Communication"

        details.append({
            "question": question,
            "topic": matched_topic,
            "category": category,
            "round_number": matched_round_num,
            "round_type": matched_round_type,
            "difficulty": None,
        })

    return details


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
        pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
        for match in re.finditer(pattern, normalized_text):
            context_start = max(
                normalized_text.rfind("\n", 0, match.start()),
                normalized_text.rfind(".", 0, match.start()),
                normalized_text.rfind("!", 0, match.start()),
                normalized_text.rfind("?", 0, match.start()),
            ) + 1
            preceding_text = normalized_text[context_start:match.start()].strip()

            if re.search(r"\b(?:not|never|hardly)(?:\s+very)?\s*$", preceding_text):
                continue
            if not re.search(r"\b(?:difficulty|round|interview|questions?)\b", preceding_text):
                continue
            if canonical not in found:
                found.append(canonical)

    return found


def apply_contextual_difficulty(text: str, rounds: list, question_details: list):
    values = extract_difficulty(text)
    if len(values) == 1:
        for r in rounds:
            r["difficulty"] = values[0]
        for q in question_details:
            q["difficulty"] = values[0]
        return

    if not values:
        return

    blocks = _split_into_blocks(text)
    for block in blocks:
        block_text = "\n".join(block.get("lines", []))
        block_diff = extract_difficulty(block_text)
        if block_diff:
            diff_val = block_diff[0]
            r_num = block.get("round_number")
            r_type = block.get("round_type")
            for r in rounds:
                if (r_num is not None and r.get("round_number") == r_num) or (
                    r_num is None and r_type and r.get("round_type") == r_type
                ):
                    r["difficulty"] = diff_val

            for qd in question_details:
                if (r_num is not None and qd.get("round_number") == r_num) or (
                    r_num is None and r_type and qd.get("round_type") == r_type
                ):
                    qd["difficulty"] = diff_val


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

        if re.match(r"^(?:student\s+)?feedback\s*[:\-–—―−]", lower):
            in_feedback_section = True
            value = re.sub(r"^(?:student\s+)?feedback\s*[:\-–—―−]\s*", "", line, flags=re.IGNORECASE).strip(" .;:!?")
            if value and value not in feedback:
                feedback.append(value)
            continue

        if in_feedback_section and re.match(
            r"^(?:difficulty|company|batch|package|role|eligibility|recruitment|round|rounds?|"
            r"l1\s*,?\s*l2|l2\s*,?\s*l1|questions?|technical\s+interview)\s*[:\-–—―−]?",
            lower,
        ):
            in_feedback_section = False
            continue

        if in_feedback_section:
            clean = line.strip(" .;:!?")
            if clean and clean not in feedback and not re.match(r"^(?:l1|l2|questions?)\b", clean.lower()):
                feedback.append(clean)

    if not feedback:
        markers = [
            "friendly", "resume based", "resume", "time consuming",
            "follow-up", "follow up", "no coding on paper", "no coding",
            "very friendly", "mostly resume", "only resume", "interviewer",
        ]
        sentences = re.split(r"(?<=\.)\s+|\n+", text)
        for sentence in sentences:
            clean = sentence.strip()
            if not clean:
                continue
            lower = clean.lower()
            if re.match(r"^(?:difficulty|company|role|package|eligibility|batch|round|rounds?|topics?|l1|l2|questions?)\s*[:\-–—―−]?", lower):
                continue
            if not any(marker in lower for marker in markers):
                continue
            if re.search(r"\b(?:what|why|how|difference between|explain|find|reverse|write|tell me about yourself)\b", lower):
                continue
            clean = clean.strip(" .;:!?")
            if clean and clean not in feedback:
                feedback.append(clean)

    return feedback


def extract_explicit_field_values(text: str, field_names):
    if not text:
        return []
    results = []
    field_pattern = "|".join(re.escape(field) for field in field_names)
    next_section_pattern = (
        r"(?:company|rounds?|stage|question|questions|"
        r"difficulty|feedback|role|package|eligibility|"
        r"code|dept|department|l1|l2)"
    )
    pattern = re.compile(
        rf"(?:^|\n|\s)(?:{field_pattern})\s*[:\-–—―−]\s*(.*?)(?=\s+{next_section_pattern}\s*[:\-–—―−]|\n|$)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        value = match.group(1).strip()
        if value:
            results.append(value)
    return results


# =========================================================
# MAIN NLP EXTRACTION ENTRY POINT
# =========================================================

def extract_information(text: str):
    """
    Main NLP extraction function.
    Returns the exact structure expected by the storage and API pipeline.
    """
    company = extract_company_name(text)
    role = extract_role(text)
    rounds = extract_rounds(text)

    topic_details = extract_preparation_topic_details(text, rounds)
    if topic_details:
        topics = list(dict.fromkeys(detail["topic"] for detail in topic_details))
    else:
        topics = extract_topics(text)

    difficulty = extract_difficulty(text)
    questions = extract_questions(text)
    question_details = extract_question_details(
        questions,
        topic_details,
        text,
        rounds,
    )
    apply_contextual_difficulty(text, rounds, question_details)
    feedback = extract_feedback(text)

    info = {
        "company": company,
        "minimum_cgpa": extract_cgpa(text),
        "maximum_backlogs": extract_backlogs(text),
        "branch_eligibility": extract_branch_eligibility(text),
        "other_criteria": extract_other_eligibility(text),
        "batch": extract_batch(text),
        "year": extract_year(text),
        "package": extract_package(text),
        "rounds": rounds,
        "topics": topics,
        "topic_details": topic_details,
        "difficulty": difficulty,
        "questions": questions,
        "question_details": question_details,
        "feedback": feedback,
    }

    if role:
        info["job_role"] = role

    return info
