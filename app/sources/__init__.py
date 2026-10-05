from app.sources.base import JobSource
from app.sources.djinni import DjinniSource
from app.sources.dou import DouSource

ALL_SOURCES: dict[str, JobSource] = {s.name: s for s in (DouSource(), DjinniSource())}

__all__ = ["ALL_SOURCES", "JobSource"]
