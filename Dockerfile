# Build stage
FROM python:3.11-slim-buster AS python

FROM python AS python-build-stage

COPY ./src/requirements.txt .

RUN pip install --upgrade pip

RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r requirements.txt

# Runtime stage
FROM python AS python-run-stage

WORKDIR /app

COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./src .

EXPOSE 8000

CMD [ "uvicorn", "--host", "0.0.0.0", "main:app" ]
