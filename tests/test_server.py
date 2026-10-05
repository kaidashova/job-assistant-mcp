from mcp.client import Client

from app.server import build_server


async def test_lists_expected_tools(services):
    async with Client(build_server(services)) as client:
        names = {t.name for t in (await client.list_tools()).tools}
    assert names == {
        "search_jobs",
        "get_job",
        "match_job_to_profile",
        "save_job",
        "update_status",
        "list_applications",
        "set_profile",
        "get_profile",
    }


async def test_full_flow_over_mcp(services, profile_kwargs):
    async with Client(build_server(services)) as client:
        await client.call_tool("set_profile", profile_kwargs)
        res = await client.call_tool("search_jobs", {"keywords": ["python", "AI"]})
        data = res.structured_content
        best = data["jobs"][0]
        assert data["scored_against_profile"] and best["score"] > 0

        await client.call_tool("save_job", {"job_id": best["job_id"]})
        await client.call_tool("update_status", {"job_id": best["job_id"], "status": "applied"})
        apps = (await client.call_tool("list_applications", {})).structured_content
        assert apps["counts"] == {"applied": 1}

        pipeline = await client.read_resource("jobs://pipeline")
        assert best["job_id"] in pipeline.contents[0].text


async def test_domain_errors_are_clean_tool_errors(services):
    async with Client(build_server(services)) as client:
        res = await client.call_tool("get_job", {"job_id": "missing"})
    assert res.is_error and "Unknown job_id" in res.content[0].text


async def test_prompts_available(services):
    async with Client(build_server(services)) as client:
        names = {p.name for p in (await client.list_prompts()).prompts}
    assert names == {"find_best_jobs", "prepare_application"}


async def test_tools_publish_output_schemas(services):
    async with Client(build_server(services)) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    schema = tools["search_jobs"].output_schema
    assert "jobs" in schema["properties"] and "total_found" in schema["properties"]
    assert tools["match_job_to_profile"].output_schema is not None
    assert tools["get_job"].annotations.read_only_hint is True
