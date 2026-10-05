from mcp_types import ToolAnnotations

INSTRUCTIONS = """\
Job-search assistant backed by real job boards (DOU and Djinni) \
and a local SQLite database.

Typical flow: set_profile once (skills, years of experience, projects) -> search_jobs \
(results are already scored against the profile) -> match_job_to_profile for a detailed \
breakdown -> save_job / update_status to track the pipeline. job_id values only come from \
search_jobs results."""

TOOL_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False)

TOOL_WRITES_LOCAL = ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=True)

TOOL_SEARCH = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=True)
