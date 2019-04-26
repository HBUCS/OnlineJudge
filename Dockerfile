FROM python:3.7-stretch

ENV OJ_ENV production

ADD . /app
WORKDIR /app

HEALTHCHECK --interval=5s --retries=3 CMD python2 /app/deploy/health_check.py

RUN apt-get update && apt-get install -y \
    nginx \
    openssl \
    curl \
    unzip \
    supervisor \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    build-essential \
    libffi-dev \
    lua5.3 \
    libfuzzy-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /app/deploy/requirements.txt

ENTRYPOINT /app/deploy/entrypoint.sh
