FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install git+https://github.com/joelmills2/evidently.git@main#egg=evidently

COPY ./api/dashboard /app/api/dashboard
COPY ./scripts /app/scripts
COPY ./src /app/src
COPY ./config /app/config

RUN mkdir -p /app/workspace

ENV FLASK_APP=api/dashboard/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONPATH=/app

EXPOSE 5002

CMD ["flask", "run", "--port=5002"]