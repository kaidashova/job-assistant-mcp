# Job Assistant MCP

An [MCP](https://modelcontextprotocol.io) server that turns Claude into a job-search assistant.
It pulls **real postings from public job boards**, scores them against **your own stored profile**
(skills, experience, projects) and tracks your applications in **SQLite**.

> *"Find remote Python + AI jobs posted this week and tell me which three fit me best."*

## What it does

| Tool | Purpose |
|---|---|
| `set_profile` / `get_profile` | Store your skills, years of experience, target roles, summary and projects (merged, so you can update one field at a time). |
| `search_jobs` | Query all boards **concurrently**, filter by keywords / remote / recency, dedupe, cache. If a profile exists every result gets a 0-100 fit score and the list is sorted best-first. |
| `match_job_to_profile` | Explainable breakdown for one posting: matched & missing skills, seniority fit, which of *your projects* to mention. |
| `get_job` | Full posting text + your application status. |
| `save_job`, `update_status`, `list_applications` | Application tracker (`saved → applied → screening → interview → offer / rejected / withdrawn`) with full status history and per-stage counts. |

Also exposed: resources `profile://me` and `jobs://pipeline`, and prompts `find_best_jobs` and
`prepare_application` (tailored cover letter + talking points).

### Job sources

| Source | Access | Notes |
|---|---|---|
| [DOU](https://jobs.dou.ua) | official public RSS | Ukrainian IT jobs |
| [Djinni](https://djinni.co) | official public RSS | Ukrainian / European IT jobs |

The scope is intentionally limited to these two Ukrainian IT job boards. LinkedIn is not
supported: it has no public job API and scraping it violates its Terms of Service. New sources are
easy to add, see [Adding a source](#adding-a-source).

A failing board never breaks a search; its error is reported in `errors` and the rest still return.

## Quick start

You need [Docker](https://www.docker.com/products/docker-desktop/) and an MCP client such as
[Claude Code](https://docs.claude.com/en/docs/claude-code).

**1. Start the server**

```bash
git clone https://github.com/kaidashova/job-assistant-mcp.git && cd job-assistant-mcp
docker compose up -d --build
```

The MCP endpoint is now at `http://localhost:8000/mcp`. If port 8000 is taken, pick another one:
`HOST_PORT=8765 docker compose up -d --build` (use the same port in step 2).

**2. Connect your MCP client**

```bash
claude mcp add --transport http job-assistant http://localhost:8000/mcp
claude mcp list        # job-assistant should show as connected
```

Then start `claude` and type `/mcp` to see the 8 tools. Any other MCP client that supports
Streamable HTTP can use the same URL.

**3. Day-to-day**

```bash
docker compose logs -f     # watch the server
docker compose down        # stop (your data is kept)
docker compose down -v     # stop and delete all data (profile, applications)
```

The container restarts automatically with Docker. Your profile and applications live in the
`job-data` Docker volume, so they survive restarts and rebuilds.

The port is bound to `127.0.0.1` only. There is no authentication, so don't expose it publicly
without a reverse proxy in front.

## Try it

1. Tell Claude about yourself once:
   > *Save my profile: skills Python, FastAPI, PostgreSQL, Docker, LLM, RAG, MCP; 3 years of
   > experience; I want Python Developer or AI Engineer roles. Projects: "Job Assistant MCP"
   > (MCP server, tech: python, sqlite, mcp), "Docs Q&A bot" (tech: python, rag, postgresql).*
2. Use the **`find_best_jobs`** prompt, or just ask:
   > *Find remote Python + AI jobs posted this week and tell me which three fit me best.*
3. > *Save the first one and mark it as applied.* → later: *"What's in my pipeline?"*

## How scoring works

Deterministic and explainable, so Claude can reason over the parts instead of a black box:

`score = 65 × skill coverage + 20 × role fit + 15 × seniority fit`

* **Skill coverage**: skills are extracted from the posting using a vocabulary of ~90 technologies
  with aliases (`k8s → kubernetes`, `postgres → postgresql`; ambiguous words like *go* only match as
  `golang`). Skills in the title/tags count double. Umbrella skills are implied (LLM/RAG ⇒ AI,
  PostgreSQL ⇒ SQL). Skills outside the vocabulary that you list in your profile are still searched for.
* **Role fit**: word overlap between your target roles and the job title.
* **Seniority fit**: level from the title (junior … lead) vs. your years of experience.

## Architecture

Layered, with dependencies pointing downward only:

```
server/         MCP adapters: tools, resources, prompts (validate input -> call service -> typed output)
   ↓
services/       business logic: SearchService, TrackerService, ProfileService, MatchingService
   ↓
repositories/   SQLite access only: Database, JobRepository, ApplicationRepository, ProfileRepository
sources/        one module per job board, all behind the same JobSource protocol
matching/       pure scoring engine + skill extraction (no I/O)
utils/          small stateless helpers (HTML to text, date parsing)
schemas/        Pydantic models shared by every layer; tool results are typed, so the server
                publishes JSON output schemas for each tool
constants/      all module-level constants (skill vocabulary, scoring weights, feed URLs, SQL schema…)
config.py       Settings (pydantic BaseSettings, read from env / .env)
container.py    composition root: builds the repositories and services and wires them together
errors.py       JobAssistantError, surfaced to the model as a clean tool error
```

```
app/
  config.py  container.py  errors.py
  constants/      skills, matching, sources, search, database, server
  schemas/        job, application, profile, search, matching, source
  repositories/   database, jobs, applications, profile
  services/       search, tracker, profile, matching, filters
  matching/       scoring, skills
  sources/        base, rss, dou, djinni
  utils/          text (HTML cleanup, remote detection), dates
  server/         app, tools, resources, prompts
tests/            offline: mocked HTTP + fixtures, one test module per layer, plus end-to-end over MCP
```

Services never import MCP and the server never touches SQL, so each layer is testable on its own.

## Development

```bash
make install   # local .venv with dev tools (uv)
make test      # offline tests, no network needed
make lint      # ruff + mypy
```

CI (GitHub Actions) runs lint + tests on Python 3.11-3.13 and builds the Docker image.

### Adding a source

Create `app/sources/mysource.py` with a class that has a `name` and an
`async fetch(client, query) -> list[Job]`, then register it in `sources/__init__.py`. Filtering by
keyword / remote / date is done centrally in `services/filters.py`, so a source only needs to fetch and map
fields. Add a fixture and a test in `tests/`.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `JOB_ASSISTANT_DB` | `/data/jobs.db` in Docker | SQLite file |
| `MCP_TRANSPORT` | `streamable-http` in `docker-compose.yml` | `stdio` or `streamable-http` |
| `MCP_HOST` / `MCP_PORT` | `0.0.0.0` / `8000` in Docker | HTTP bind address inside the container |
| `JOB_ASSISTANT_HTTP_TIMEOUT` | `20` | Seconds before a job-board request times out |

To change one, add it under `environment:` in `docker-compose.yml` and run `docker compose up -d` again.

## Notes

* Built on the official MCP Python SDK (v2, `MCPServer`).
* Be a good citizen: only public feeds/APIs are used, with a descriptive User-Agent and one request
  per board per search.
* Your profile and applications never leave your machine; only the search keywords go to the boards.

MIT licensed.
