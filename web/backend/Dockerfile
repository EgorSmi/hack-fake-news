# syntax=docker/dockerfile:1
FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY run_app.py run_app.py
COPY . .
CMD python run_app.py