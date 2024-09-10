# Build stage
FROM python:3.11-slim-buster AS builder

WORKDIR /app

COPY ./src/requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

COPY ./src .

# Runtime stage
FROM python:3.11-slim-buster AS runner

WORKDIR /app

COPY --from=builder /app .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD [ "uvicorn", "--host", "0.0.0.0", "main:app" ]
