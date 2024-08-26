FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api/ingestion /app/api/ingestion
COPY ./src/utils /app/src/utils
COPY ./config /app/config

ENV PYTHONPATH=/app
ENV FLASK_APP=/app/api/ingestion/app.py

EXPOSE 5001

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5001"]