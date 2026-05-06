FROM python:3.9-slim-buster

ARG PIP_EXTRA_INDEX_VALUE

ARG PIP_TRUSTED_HOST_VALUE

ENV PIP_EXTRA_INDEX_URL $PIP_EXTRA_INDEX_VALUE

ENV PIP_TRUSTED_HOST $PIP_TRUSTED_HOST_VALUE

# Install Node.js to provide a JavaScript runtime
RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python","app.py"]
