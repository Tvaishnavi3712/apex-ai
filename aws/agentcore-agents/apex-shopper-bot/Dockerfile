FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# Copy agent code
COPY agent.py ./

# Expose port for AgentCore
EXPOSE 8080

# Run the agent
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]
