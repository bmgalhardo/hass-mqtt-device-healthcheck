FROM python:3.12-slim as builder

RUN apt update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR='/tmp/poetry_cache' \
    POETRY_HOME='/usr/local'

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

FROM python:3.12-slim  as runtime

ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH" \
    PYTHONPATH="/code"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src/app /code/app