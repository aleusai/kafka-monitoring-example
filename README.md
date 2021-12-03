# Introduction

This repository is an example of a use case where Apache Kafka is used to process real time information. 

It comprises of the basic setup of a Kafka "cluster" with the Zookeeper backend, a Kafka producer and a Kafka 
consumer.

In particular it simulates a stream of calls (created by the producer) which are then consumed by the consumer, which  
aggregates the information to obtain the total number of calls and the total calls duration.
The producer assumes a Poisson distribution for the number of calls and an Exponential distribution for the duration of 
calls. The calls are generated continuously so the overall calls rate is higher than the simple Poisson mean, say X call per minute, as these are created and submitted with a very small delay (to simulate high load): an environment variable allows the tweak of the calls rate by reducing the batch size (number of calls per minute). 

The consumer then exposes these metrics through a (Prometheus) http endpoint.
Both the consumer and the producer also expose their health_status metric.

The consumer also prints to the output file `faust_consumer.out.log` the records of the calls that lasted more than 60s, 
which can be read through docker.

The producer and consumer together with the two mentioned metrics are monitored with the following monitoring stack:

1. Prometheus server
2. Prometheus alertmanager
3. Grafana

# Setup

All the services are provisioned with docker-compose in docker containers. 
The python Faust library is used for the consumer: this allows the use on the consumer side 
of a global table for the records aggregation, so that the consumer end can be scaled up to many workers/consumers.

Faust also exposes an http endpoint to publich the Prometheus metrics, without the need e.g. for an extra Flask webframework.

Three producers are built that use each different libraries/setups: 
- a producer that uses Faust
- one that uses python-kafka and Quart
- and finally one that uses python kafka confluent also with Quart (this one is meant to be more performing)

Feel free to comment out in the docker-compose file the producers you do not want to start.


Both the producer and the consumer are run wth the supervisor framework, with the option to be constantly restarted 
in case of a crash: this guarantees that the processes can withstand temporary blackouts or e.g. when no Kafka broker 
is yet available e.g. at startup.
  
Grafana visualizes the metrics with a pre-created ad hoc dashboard. Alerts are also present in Prometheus on 
the health status of the producer and consumer, as well as on the two main metrics, which are then picked up by the 
Prometheus alertmanager.

In order to build all the containers run

`. dc-up.sh`

To bring down all the containers run 

`. dc-down.sh`

After starting up all the containers, the producer and consumer can be reached at the following url:

localhost:6067/metrics (producer)  
localhost:6066/metrics (consumer) 

while in the docker network they are scraped by the Prometheus server at the following utls:

faust_producer:6066/metrics (producer)  
faust_consumer:6066/metrics (consumer) 

Prometheus could also monitor the Kafka broker and Zookeeper through the jmx native Prometheus exporter 
available for Kafka, but it is commented out in the Prometheus configuration file for the time being (to be tested).

All the docker containers themselves could also be monitored through a docker cadvisor container: in the current version 
of the docker-compose file this is not present. 

# Testing

In the future a pytest set of tests will be made available (work in progress).

