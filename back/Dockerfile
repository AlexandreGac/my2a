# syntax=docker/dockerfile:1

FROM python:3.11.6-bookworm as build-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    # Env
    PYSETUP_PATH="/opt/pysetup"

# Install Poetry
RUN pip install --no-cache-dir poetry==1.6.1

WORKDIR $PYSETUP_PATH

COPY pyproject.toml ./

# Pipefail to ensure build files if something goes wrong
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN poetry add django-solo && poetry install --no-dev --no-root --no-cache
# ====================== RUNTIME ENVIRONMENT ======================
FROM python:3.11.6-slim-bookworm as runtime-base
ENV PYSETUP_PATH="/opt/pysetup" \
    PATH="/opt/pysetup/.venv/bin:$PATH" \
    # Python
    PYTHONUNBUFFERED=1

WORKDIR /src

COPY --from=build-base $PYSETUP_PATH $PYSETUP_PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # For checking when db is up
    netcat-traditional=1.10-47 \
    # Add postgresql support
    python3-psycopg2=2.9.5-1+b1 \
    && rm -rf /var/lib/apt/lists/*

# ======================== DEV ENVIRONMENT ========================
# `development` image is used during development / testing
FROM runtime-base as development

COPY ./entrypoint-dev.sh /usr/local/bin/
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint-dev.sh \
    && chmod +x /usr/local/bin/entrypoint-dev.sh

ENTRYPOINT ["/usr/local/bin/entrypoint-dev.sh"]

# ======================== PROD ENVIRONMENT ========================
# `production` image is used in production
FROM runtime-base as production

COPY ./entrypoint-prod.sh /usr/local/bin/
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint-prod.sh \
    && chmod +x /usr/local/bin/entrypoint-prod.sh

ENTRYPOINT ["/usr/local/bin/entrypoint-prod.sh"]
