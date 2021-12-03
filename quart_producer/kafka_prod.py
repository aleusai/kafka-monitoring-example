import os
import sys
import logging
import time
from json import dumps
from kafka import KafkaProducer
import asyncio
from message_builder import get_calls_info
from health_status import health_status


server_name = os.environ.get('BROKER_HOST_NAME', 'localhost')
server_port = os.environ.get('BROKER_HOST_PORT', '29092')
topic = os.environ.get('KAFKA_TOPIC', 'calls')

try:
    producer = KafkaProducer(bootstrap_servers=[''.join([server_name, ':', server_port])],
                        value_serializer=lambda x:
                        dumps(x).encode('utf-8'))
except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print('There was an error with the broker', 
        exc_type, fname, exc_tb.tb_lineno) 

def on_send_success(record_metadata):
    print('Successful sent to topic {} with partition {} and offset {}'\
        .format(record_metadata.topic, record_metadata.partition, record_metadata.offset))

def on_send_error(excp):
    logging.error('There was an error sending messages to the Brokers', exc_info=excp)
    global health_status
    health_status = 0

async def kafka_producer():

    global health_status
    while True:
        messages_list = get_calls_info()
        batch_len = len(messages_list)
        start = time. time()
        for message in messages_list:
            caller_phone_number = message['key']
            call_info = message['value']
            
            try:
                producer.send(topic, key=bytes(caller_phone_number, 'ascii'), value=call_info)\
                    .add_callback(on_send_success).add_errback(on_send_error)
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('There was an error connecting to the broker', 
                    exc_type, fname, exc_tb.tb_lineno) 
                health_status = 0

        producer.flush()
        batch_time = time. time() - start 
        print(f'************ batch_len {batch_len} time {batch_time}', )
        health_status = 1      
        await asyncio.sleep(0.1) # without this quart does not respond i.e. no monitoring
    