FROM python:3.9-slim-buster

ARG PIP_EXTRA_INDEX_VALUE

ARG PIP_TRUSTED_HOST_VALUE

ENV PIP_EXTRA_INDEX_URL $PIP_EXTRA_INDEX_VALUE

ENV PIP_TRUSTED_HOST $PIP_TRUSTED_HOST_VALUE

# Install Node.js to provide a JavaScript runtime
# Install Node.js to provide a JavaScript runtime
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security/d' /etc/apt/sources.list && \
    apt-get update

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","app.py"]
