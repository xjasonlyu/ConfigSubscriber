FROM python:3-alpine

COPY ./requirements.txt /requirements.txt
COPY ./subscribe /subscribe
COPY ./main.py /main.py

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

ENTRYPOINT ["python", "/main.py"]
