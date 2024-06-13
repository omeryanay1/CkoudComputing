FROM python:3.12.2-slim as base
WORKDIR ./app
COPY main.py .
COPY BooksCollection.py .
COPY RatingsCollection.py .
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt
EXPOSE 8000 
CMD ["python3", "main.py"]
