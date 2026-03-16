FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/mcp

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
RUN uv pip install --system --no-cache -r pyproject.toml

COPY src/ ./src/
RUN uv pip install --system --no-cache -e .

EXPOSE 8102

CMD ["python", "-m", "mcp_server"]
