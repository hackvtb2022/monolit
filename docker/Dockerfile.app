FROM python:3.9-slim

ENV APP_HOME=/app

WORKDIR $APP_HOME

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app $APP_HOME/

CMD []