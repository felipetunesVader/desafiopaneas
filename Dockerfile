
FROM python:3.10-slim


WORKDIR /app


COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY ./app .


EXPOSE 80


ENV LOG_DIR /app/logs


RUN mkdir -p ${LOG_DIR}


ENV PYTHONUNBUFFERED 1


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
