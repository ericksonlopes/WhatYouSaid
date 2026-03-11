# Use official Python image
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install --no-cache-dir .

CMD ["python", "main.py"]

