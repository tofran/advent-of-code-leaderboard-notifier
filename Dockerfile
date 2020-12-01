FROM python:alpine

RUN pip install --upgrade pip && pip install requests

COPY ./advent_of_code_notify.py ./advent_of_code_notify.py

ENTRYPOINT ["python"]
CMD ["/advent_of_code_notify.py"]