# syntax=docker/dockerfile:1
FROM python:3.7
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN python3 -m dostoevsky download fasttext-social-network-model

COPY run_app.py run_app.py
COPY . .
RUN python download_models.py
CMD python run_app.py