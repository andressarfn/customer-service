FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
    && pip install poetry==2.1.4


WORKDIR /app

COPY pyproject.toml poetry.lock ./


RUN poetry config virtualenvs.create false \
    && poetry install --no-root --without dev

COPY . .

# FINAL IMAGE #
FROM python:3.12-slim

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create the diretory for the application user
RUN mkdir -p /home/app/src && chown -R appuser:appuser /home/app

# Set environment variables
ENV  HOME=/home/app \
    APP_HOME=/home/app/src

# Create appropriate directories
WORKDIR $APP_HOME

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the project
COPY --from=builder /app $APP_HOME
RUN  chown -R appuser:appuser $APP_HOME

USER appuser
