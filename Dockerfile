# Use Python 3.13 as the base image
FROM alpine

# Set the working directory in the container
WORKDIR /app

# Copy uv installer script
COPY --from=ghcr.io/astral-sh/uv:latest /usr/bin/uv /usr/bin/uv

# Copy project files
COPY requirements.txt ./
COPY src/ ./src/

# Create the data directory (for persistent database files) and nstall dependencies using uv
RUN mkdir -p data && uv pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run log_ingestor.py with uvicorn when the container launches
# --host 0.0.0.0 is important to make it accessible from outside the container
CMD ["uvicorn", "src.log_ingestor:app", "--host", "0.0.0.0", "--port", "8000"]