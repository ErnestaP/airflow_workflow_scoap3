FROM apache/airflow:latest-python3.7

USER root
RUN apt-get update && \
    apt-get -y install libleveldb-dev libssl-dev libkrb5-dev git
ENV AIRFLOW_UID=501
ENV FTP_HOST=ukftp.oup.com
ENV FTP_USER=scoapuser2
ENV FTP_PASSWORD=Ux$2FtP2
ENV ENDPOINT=https://s3.cern.ch
ENV ACCESS_KEY=84bdbd7c1c05477eaf6993439fc73953
ENV SECRET_KEY=7033cee4acc349058756b34698fa8068
ENV BUCKET_NAME=scoap3-test-ernesta
USER airflow
RUN pip install --no-cache-dir plyvel \
    zipfile36 \
    wheel \
    python-dotenv==0.19.2 \
    boto3==1.20.15 \
    zipfile36==0.1.3 \
    ftputil==5.0.1 \ 
    scrapy \
    autosemver\
    git+https://github.com/SCOAP3/hepcrawl.git@python3-compatible
