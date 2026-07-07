FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn>=0.29"

COPY server.py .
COPY static/ static/

EXPOSE 3940

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3940"]
