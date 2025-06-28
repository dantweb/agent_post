FROM python:3.9-slim

# Install system dependencies needed to build gevent and psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libpq-dev \
    build-essential \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
