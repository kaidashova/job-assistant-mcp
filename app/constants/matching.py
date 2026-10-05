import re

LEVELS = ["intern", "junior", "middle", "senior", "lead"]

# (level index, title pattern); checked in order, first hit wins
TITLE_LEVEL_PATTERNS = [
    (4, r"\b(lead|principal|staff|head|architect|director)\b"),
    (3, r"\b(senior|sr\.?)\b"),
    (1, r"\b(junior|jr\.?|trainee|entry)\b"),
    (0, r"\b(intern|internship)\b"),
    (2, r"\b(middle|mid|mid-level|regular)\b"),
]

# (years of experience below which the level applies, level index); anything above is the top level
PROFILE_LEVEL_YEAR_LIMITS = [(1, 0), (2, 1), (4, 2), (7, 3)]
TOP_LEVEL = len(LEVELS) - 1

SKILLS_WEIGHT = 65
ROLE_WEIGHT = 20
SENIORITY_WEIGHT = 15

TITLE_SKILL_MULTIPLIER = 2  # skills named in the title/tags count double

# used when there is nothing to compare, so a missing signal is neither a bonus nor a penalty
NEUTRAL_SKILL_RATIO = 0.4
NEUTRAL_ROLE_RATIO = 0.5
NEUTRAL_SENIORITY_RATIO = 0.7

SENIORITY_RATIO_BY_LEVEL_GAP = {0: 1.0, 1: 0.5}  # larger gaps score 0
UNDERQUALIFIED_GAP_NOTE_FROM = 2  # job this many levels below the candidate gets a note

VERDICT_THRESHOLDS = [(75, "strong match"), (55, "good match"), (35, "partial match")]
WEAK_VERDICT = "weak match"

ROLE_WORD_PATTERN = re.compile(r"[a-z+#.]+")
