FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

ENV PORT=8080
ENV MCP_BASE_URL=""

EXPOSE 8080

CMD ["python", "-m", "ga4_mcp"]
