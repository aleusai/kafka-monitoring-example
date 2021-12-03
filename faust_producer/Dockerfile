FROM ubuntu:20.04
RUN apt-get update -y && \
    apt-get -y upgrade && \
    apt-get install -y python3-pip python-dev && \
    apt-get install -y supervisor

RUN mkdir -p /var/log/supervisor

COPY ./common/message_builder.py /message_builder.py
COPY ./faust_producer/faust_producer.py /faust_producer.py
COPY ./faust_producer/requirements.txt /requirements.txt
RUN /usr/bin/pip3 install -r requirements.txt
CMD ["/usr/bin/supervisord"]
