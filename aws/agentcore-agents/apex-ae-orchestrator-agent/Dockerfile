# Apex Agentic Enterprise OrchestratorAgent — AgentCore container
# Multi-stage so the runtime image stays small.
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target /build/vendor -r requirements.txt

# ---------------------------------------------------------------------------
FROM public.ecr.aws/docker/library/python:3.12-slim AS runtime

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/vendor

COPY --from=builder /build/vendor /app/vendor
COPY agent.py /app/agent.py
COPY __init__.py /app/__init__.py
# NOTE: synthetic-data files (data/) are bundled into the AgentCore ZIP at
# deploy time by ../deploy_ae_agents.py — they are NOT in the Docker build
# context. This Dockerfile is for local-test smoke runs only; AgentCore uses
# the S3 ZIP path, not this image.

EXPOSE 8080

CMD ["python", "agent.py"]
