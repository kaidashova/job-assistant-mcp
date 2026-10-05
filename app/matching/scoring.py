import re

from app.constants.matching import (
    LEVELS,
    NEUTRAL_ROLE_RATIO,
    NEUTRAL_SENIORITY_RATIO,
    NEUTRAL_SKILL_RATIO,
    PROFILE_LEVEL_YEAR_LIMITS,
    ROLE_WEIGHT,
    ROLE_WORD_PATTERN,
    SENIORITY_RATIO_BY_LEVEL_GAP,
    SENIORITY_WEIGHT,
    SKILLS_WEIGHT,
    TITLE_LEVEL_PATTERNS,
    TITLE_SKILL_MULTIPLIER,
    TOP_LEVEL,
    UNDERQUALIFIED_GAP_NOTE_FROM,
    VERDICT_THRESHOLDS,
    WEAK_VERDICT,
)
from app.matching.skills import expand_skills, extract_skills, normalize_skill, term_pattern
from app.schemas import Job, MatchResult, Profile, ProjectRelevance, ScoreBreakdown


def job_level(title: str) -> int | None:
    t = title.lower()
    for level, pattern in TITLE_LEVEL_PATTERNS:
        if re.search(pattern, t):
            return level
    return None


def profile_level(years: float | None) -> int | None:
    if years is None:
        return None
    for limit, level in PROFILE_LEVEL_YEAR_LIMITS:
        if years < limit:
            return level
    return TOP_LEVEL


def _verdict(score: int) -> str:
    for threshold, label in VERDICT_THRESHOLDS:
        if score >= threshold:
            return label
    return WEAK_VERDICT


def match_job(job: Job, profile: Profile) -> MatchResult:
    profile_skills = expand_skills({normalize_skill(s) for s in profile.skills})
    text = f"{job.title}\n{' '.join(job.tags)}\n{job.description}"
    job_skills = extract_skills(text, extra_terms=sorted(profile_skills))
    title_skills = extract_skills(f"{job.title} {' '.join(job.tags)}", sorted(profile_skills))

    matched = sorted(job_skills & profile_skills)
    missing = sorted(job_skills - profile_skills)

    # skills named in the title/tags count double: they are what the role is *about*
    weight = {s: TITLE_SKILL_MULTIPLIER if s in title_skills else 1 for s in job_skills}
    total = sum(weight.values())
    skill_ratio = sum(weight[s] for s in matched) / total if total else NEUTRAL_SKILL_RATIO
    notes: list[str] = []
    if not job_skills:
        notes.append("No known tech skills detected in the posting; skill score is neutral.")

    # role fit: best word-overlap between a target role and the job title
    role_ratio = NEUTRAL_ROLE_RATIO
    if profile.target_roles:
        title_words = set(ROLE_WORD_PATTERN.findall(job.title.lower()))
        role_ratio = max(
            len(set(ROLE_WORD_PATTERN.findall(r.lower())) & title_words)
            / max(len(set(ROLE_WORD_PATTERN.findall(r.lower()))), 1)
            for r in profile.target_roles
        )

    # seniority fit
    jl, pl = job_level(job.title), profile_level(profile.years_experience)
    if jl is None or pl is None:
        seniority_ratio = NEUTRAL_SENIORITY_RATIO
    else:
        seniority_ratio = SENIORITY_RATIO_BY_LEVEL_GAP.get(abs(jl - pl), 0.0)
        if jl > pl:
            notes.append(f"Posting looks {LEVELS[jl]}-level; your experience suggests {LEVELS[pl]}.")
        elif pl - jl >= UNDERQUALIFIED_GAP_NOTE_FROM:
            notes.append(f"Posting looks {LEVELS[jl]}-level, below your {LEVELS[pl]} experience.")

    score = round(SKILLS_WEIGHT * skill_ratio + ROLE_WEIGHT * role_ratio + SENIORITY_WEIGHT * seniority_ratio)

    # which of the user's projects back this posting up?
    projects = []
    for p in profile.projects:
        tech = {normalize_skill(t) for t in p.tech}
        text_hits = {t for t in tech if term_pattern(t).search(text)}
        overlap = sorted((tech & job_skills) | text_hits)
        if overlap:
            projects.append(ProjectRelevance(name=p.name, description=p.description, relevant_tech=overlap))
    projects.sort(key=lambda p: -len(p.relevant_tech))

    score = max(0, min(100, score))
    return MatchResult(
        job_id=job.id,
        title=job.title,
        company=job.company,
        url=job.url,
        score=score,
        verdict=_verdict(score),
        matched_skills=matched,
        missing_skills=missing,
        breakdown=ScoreBreakdown(
            skills=round(SKILLS_WEIGHT * skill_ratio),
            role=round(ROLE_WEIGHT * role_ratio),
            seniority=round(SENIORITY_WEIGHT * seniority_ratio),
        ),
        relevant_projects=projects,
        notes=notes,
    )
