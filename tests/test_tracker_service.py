import pytest
from conftest import search

from app.errors import JobAssistantError
from app.schemas import Status


async def first_job_id(services) -> str:
    return (await search(services, "python", "AI")).jobs[0].job_id


async def test_lifecycle_with_history(services):
    job_id = await first_job_id(services)

    saved = services.tracker.save(job_id, "looks great")
    assert saved.application.status == Status.SAVED and not saved.already_saved
    assert services.tracker.save(job_id).already_saved is True

    app = services.tracker.update_status(job_id, "Applied", "sent CV")
    assert app.status == Status.APPLIED and app.notes == "sent CV"
    assert [h.status for h in app.history] == [Status.SAVED, Status.APPLIED]

    pipeline = services.tracker.pipeline()
    assert pipeline.counts == {"applied": 1}
    assert services.tracker.pipeline("saved").applications == []


async def test_notes_kept_when_not_provided(services):
    job_id = await first_job_id(services)
    services.tracker.save(job_id, "keep me")
    assert services.tracker.update_status(job_id, "applied").notes == "keep me"


async def test_update_unsaved_job_creates_application(services):
    job_id = await first_job_id(services)
    assert services.tracker.update_status(job_id, "interview").status == Status.INTERVIEW


async def test_invalid_inputs(services):
    job_id = await first_job_id(services)
    with pytest.raises(JobAssistantError, match="Invalid status"):
        services.tracker.update_status(job_id, "ghosted")
    with pytest.raises(JobAssistantError, match="Invalid status"):
        services.tracker.pipeline("ghosted")
    with pytest.raises(JobAssistantError, match="Unknown job_id"):
        services.tracker.save("nope")
