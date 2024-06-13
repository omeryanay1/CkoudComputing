FROM python:3.12.2-slim as base

WORKDIR /app

# Copy application code
COPY main.py .
COPY LoansCollection.py .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python3", "main.py"]