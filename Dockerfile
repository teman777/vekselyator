FROM python:3.8

WORKDIR /home
RUN pip install -U pip aiogram pytz && apt-get update && apt-get -y install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "veksel.py"]

