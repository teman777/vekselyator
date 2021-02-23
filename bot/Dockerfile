FROM python:3.8

WORKDIR /home
RUN pip install -U pip aiogram pytz && apt-get update && pip install -U pip mysql-connector-python
COPY *.py ./

ENV DB_PASSWORD vekselbotpassword
ENV TG_API 1575260517:AAEXiFbeffmgJXjeNg5Tkyb05EwiIgSUKFU

ENTRYPOINT ["python", "veksel.py"]

