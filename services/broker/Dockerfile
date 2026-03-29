FROM python:3.11-slim
RUN pip install --no-cache-dir poetry
WORKDIR /app
COPY pyproject.toml poetry.lock poetry.toml ./
COPY shared ./shared
COPY services/broker ./services/broker
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main
ENV PYTHONPATH=/app/services/broker
WORKDIR /app/services/broker
CMD ["python", "main.py"]
