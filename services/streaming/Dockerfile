FROM python:3.11-slim
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock poetry.toml ./
COPY shared ./shared
COPY services/streaming ./services/streaming
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main
ENV PYTHONPATH=/app/services/streaming
WORKDIR /app/services/streaming
EXPOSE 8000
CMD ["python", "main.py"]
