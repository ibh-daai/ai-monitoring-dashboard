FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api/ingestion /app/api/ingestion
COPY ./src /app/src
COPY ./config /app/config

ENV FLASK_APP=api/ingestion/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app

EXPOSE 5001

CMD ["flask", "run", "--port=5001"]