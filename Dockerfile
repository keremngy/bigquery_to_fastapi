FROM python:3.9-slim

EXPOSE 80
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY empty_key_file.json /app/empty_key_file.json
COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt
RUN pip install fastapi uvicorn

RUN pip3 install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]