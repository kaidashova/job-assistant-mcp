FROM python:3.12-slim AS build
WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    JOB_ASSISTANT_DB=/data/jobs.db \
    MCP_TRANSPORT=stdio \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000
RUN useradd --create-home --uid 1000 app && mkdir /data && chown app /data
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
USER app
VOLUME /data
EXPOSE 8000
# stdio by default (docker run -i ...); set MCP_TRANSPORT=streamable-http for a network server
ENTRYPOINT ["job-assistant"]
