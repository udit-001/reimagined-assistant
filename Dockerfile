FROM python:3.11-slim-buster AS python

WORKDIR /app

COPY ./src/requirements.txt .

RUN apt-get update && apt-get install -V -y \
   # dependencies for building Python packages
   build-essential

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY ./src .
EXPOSE 8000

CMD [ "uvicorn", "--host", "0.0.0.0", "main:app" ]
