FROM python:3.12-alpine AS poetry-base
LABEL maintainer="ohiliazov"

ENV PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.7.1

RUN adduser --disabled-password --no-create-home mmlib-user

RUN apk add  --update --no-cache curl && \
    curl -sSL https://install.python-poetry.org | python - && \
    apk del curl

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install --no-interaction --no-ansi

COPY ./mmlib /code/mmlib
COPY ./tests /code/tests

USER mmlib-user
