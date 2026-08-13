# Apex ChatSTP Router — copies all 4 specialist agent.py files into /app for
# the in-process fallback path when SPECIALIST_ARNS are not set.
FROM public.ecr.aws/docker/library/python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --target /build/vendor -r requirements.txt

FROM public.ecr.aws/docker/library/python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/vendor

COPY --from=builder /build/vendor /app/vendor

# Router's own agent.py
COPY apex-stp-chatstp-router/agent.py    /app/agent.py
COPY apex-stp-chatstp-router/__init__.py /app/__init__.py

# Sibling specialists for the in-process fallback path
COPY apex-stp-policy-agent       /app/apex-stp-policy-agent
COPY apex-stp-maintenance-agent  /app/apex-stp-maintenance-agent
COPY apex-stp-diagnostics-agent  /app/apex-stp-diagnostics-agent
COPY apex-stp-reliability-agent  /app/apex-stp-reliability-agent

EXPOSE 8080
CMD ["python", "agent.py"]
