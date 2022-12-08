FROM python:3.11-alpine

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./advent_of_code_notify.py ./advent_of_code_notify.py
CMD "./advent_of_code_notify.py"