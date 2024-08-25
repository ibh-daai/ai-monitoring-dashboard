FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install git+https://github.com/joelmills2/evidently.git@main#egg=evidently

COPY ./api/dashboard /app/api/dashboard
COPY ./scripts /app/scripts
COPY ./src/dashboard /app/src/dashboard
COPY ./src/utils /app/src/utils
COPY ./config /app/config
COPY ./frontend/dashboard/public/images /app/frontend/dashboard/public/images



RUN mkdir -p /app/workspace

ENV PYTHONPATH=/app
ENV FLASK_APP=/app/api/dashboard/app.py

EXPOSE 5002

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5002"]