from app.matching import expand_skills, extract_skills


def test_extract_skills_handles_aliases_and_symbols():
    text = "We use Postgres, k8s, C++ and Node.js; not golfing or going anywhere. REST API too."
    found = extract_skills(text)
    assert {"postgresql", "kubernetes", "c++", "node.js", "rest"} <= found
    assert "go" not in found  # bare English word must not match


def test_extract_skills_extra_terms():
    assert "dagster" in extract_skills("We orchestrate with Dagster", extra_terms=["dagster"])


def test_umbrella_skills_are_implied():
    assert {"ai", "generative ai", "sql"} <= expand_skills({"llm", "postgresql"})
