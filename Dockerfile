# ------------ Dockerfile ------------
FROM python:3.12-slim

WORKDIR /app

# Copy your FastMCP server source
COPY server/ /app/server/

# Install dependencies
RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Expose port
#EXPOSE 8000

# Environment variables (optional)
#ENV HOST=0.0.0.0 PORT=8000

# Run the FastAPI app via Uvicorn
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0"]
# ------------ end ------------
