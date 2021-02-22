FROM python:3.8

WORKDIR /home
RUN pip install -U pip aiogram pytz && apt-get update && pip install -U pip mysql-connector
COPY *.py ./

ENV DB_PASSWORD vekselbotpassword

ENTRYPOINT ["python", "veksel.py"]

