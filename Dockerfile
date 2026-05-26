FROM python:3.13.13-alpine3.22

ENV FLASK_APP=src.training_app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup -S app && adduser -S -G app app

COPY requirements.txt .
RUN apk upgrade --no-cache \
    && python -m pip install --no-cache-dir --upgrade \
        pip==26.1.1 \
        setuptools==82.0.1 \
        wheel==0.47.0 \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER app

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
