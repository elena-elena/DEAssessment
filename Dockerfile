FROM python:3.9-slim

EXPOSE 8501

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

ADD localapp app

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]