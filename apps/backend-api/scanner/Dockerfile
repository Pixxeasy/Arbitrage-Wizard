FROM python:3.12-slim
LABEL authors="Pixxeasy"

WORKDIR /app

COPY core /app/core
COPY scanner /app/scanner
COPY scanner/conf /app/conf
COPY endpoint/api/handler/ArbitrageHandler.py /app/endpoint/api/handler/ArbitrageHandler.py
COPY endpoint/api/schema/Arbitrage.py /app/endpoint/api/schema/Arbitrage.py

COPY scanner/launcher.py /app/launcher.py
COPY scanner/.env /app/.env
COPY requirements.txt /app/requirements.txt

COPY application_default_credentials.json /app/application_default_credentials.json

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "launcher.py"]