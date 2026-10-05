import re
from functools import lru_cache

from app.constants.skills import ALIAS_TO_CANON, IMPLIES, SEARCH_TERMS_OVERRIDE, VOCAB


def expand_skills(skills: set[str]) -> set[str]:
    """Add umbrella skills implied by the given ones (llm -> ai, postgresql -> sql, ...)."""
    return skills | {umbrella for umbrella, subs in IMPLIES.items() if skills & subs}


def normalize_skill(skill: str) -> str:
    s = skill.strip().lower()
    return ALIAS_TO_CANON.get(s, s)


def term_pattern(term: str) -> re.Pattern[str]:
    """Word-boundary regex that also copes with terms like c++, c#, .net, node.js."""
    return re.compile(rf"(?<![\w+#.]){re.escape(term.lower())}(?![\w+#]|\.\w)", re.IGNORECASE)


@lru_cache(maxsize=1)
def _vocab_patterns() -> list[tuple[str, re.Pattern[str]]]:
    out = []
    for canon, aliases in VOCAB.items():
        terms = SEARCH_TERMS_OVERRIDE.get(canon, [canon, *aliases])
        terms = sorted(terms, key=len, reverse=True)
        out.append((canon, re.compile("|".join(term_pattern(t).pattern for t in terms), re.I)))
    return out


def extract_skills(text: str, extra_terms: list[str] | None = None) -> set[str]:
    """Return canonical skills mentioned in text.

    ``extra_terms`` lets callers look for skills outside the built-in vocabulary
    (e.g. niche tools from the user's profile).
    """
    found = {canon for canon, pat in _vocab_patterns() if pat.search(text)}
    for term in extra_terms or []:
        if term not in VOCAB and term_pattern(term).search(text):
            found.add(term)
    return found
