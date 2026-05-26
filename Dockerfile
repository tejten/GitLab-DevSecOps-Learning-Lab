FROM python:3.13.13-slim-bookworm

ENV FLASK_APP=src.training_app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir --upgrade \
        pip==26.1.1 \
        setuptools==82.0.1 \
        wheel==0.47.0 \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

USER app

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
