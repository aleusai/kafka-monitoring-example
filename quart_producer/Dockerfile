FROM ubuntu:20.04
RUN apt-get update -y && \
    apt-get -y upgrade && \
    apt-get install -y python3-pip python-dev && \
    apt-get install -y supervisor

RUN mkdir -p /var/log/supervisor

COPY ./common/message_builder.py /message_builder.py
COPY ./common/health_status.py /health_status.py
COPY ./quart_producer/quart_producer.py /quart_producer.py
COPY ./quart_producer/requirements.txt /requirements.txt
COPY ./quart_producer/kafka_prod.py /kafka_prod.py
RUN /usr/bin/pip3 install -r requirements.txt
CMD ["/usr/bin/supervisord"]
