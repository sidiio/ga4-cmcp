FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose port for SSE
EXPOSE 8000

# Set entrypoint
CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
