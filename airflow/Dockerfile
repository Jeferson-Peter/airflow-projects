FROM apache/airflow:2.9.2

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt
#docker build . --tag extending_airflow:latest