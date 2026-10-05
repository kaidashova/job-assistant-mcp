import pytest

from app.schemas import ProfileUpdate


def test_update_merges_and_dedupes_skills(services):
    services.profile.update(ProfileUpdate(skills=["Python", "python ", "Docker"], years_experience=2))
    p = services.profile.update(ProfileUpdate(summary="hello"))
    assert p.skills == ["Docker", "Python"]
    assert p.years_experience == 2 and p.summary == "hello"


def test_projects_are_validated_models(services):
    p = services.profile.update(ProfileUpdate(projects=[{"name": "X", "tech": ["python"]}]))
    assert p.projects[0].name == "X" and p.projects[0].description == ""


def test_get_returns_none_before_first_update(services):
    assert services.profile.get() is None


def test_invalid_profile_rejected():
    with pytest.raises(ValueError):
        ProfileUpdate(years_experience=-1)
