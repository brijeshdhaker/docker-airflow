#
# docker build -t brijeshdhaker/apache-airflow:2.4.3 -f Dockerfile .
#

FROM apache/airflow:2.4.3

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends vim default-jdk \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir pyspark==3.1.2 apache-airflow-providers-apache-spark
