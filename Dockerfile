#
# docker build -t brijeshdhaker/apache-airflow:2.5.0 -f Dockerfile .
#

FROM apache/airflow:2.5.0

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends vim default-jdk \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install apache-airflow[apache.spark]==2.5.0 \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.0/constraints-3.7.txt"
