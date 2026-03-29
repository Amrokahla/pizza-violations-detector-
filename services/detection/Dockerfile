FROM python:3.11-slim
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock poetry.toml ./
COPY shared ./shared
COPY services/detection ./services/detection
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --with database,detection
ENV PYTHONPATH=/app/services/detection
WORKDIR /app/services/detection
CMD ["python", "main.py"]
