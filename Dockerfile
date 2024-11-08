FROM python:alpine

ENV PROJECT_ROOT = /app
WORKDIR $PROJECT_ROOT
ENV PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

ENTRYPOINT ["fastapi", "run"]
