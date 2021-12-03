import os
import sys
import logging
import time
from json import dumps
from confluent_kafka import Producer
import asyncio
from message_builder import get_calls_info
from health_status import health_status


server_name = os.environ.get('BROKER_HOST_NAME', 'localhost')
server_port = os.environ.get('BROKER_HOST_PORT', '29092')
topic = os.environ.get('KAFKA_TOPIC', 'calls')

try:
    producer = Producer({'bootstrap.servers': ''.join([server_name, ':', server_port])})

except:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print('There was an error with the broker', 
        exc_type, fname, exc_tb.tb_lineno) 

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

async def kafka_producer():

    global health_status
    producer.poll(0)
    while True:
        messages_list = get_calls_info()
        batch_len = len(messages_list)
        start = time. time()
        for message in messages_list:
            caller_phone_number = message['key']
            call_info = message['value']
            
            try:
                producer.produce(topic, key=caller_phone_number, value=dumps(message).encode('utf-8'), callback=delivery_report)
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('There was an error connecting to the broker', 
                    exc_type, fname, exc_tb.tb_lineno) 
                producer.poll(10)
                health_status = 0

        producer.flush()
        batch_time = time. time() - start 
        print(f'************ batch_len {batch_len} time {batch_time}', )
        health_status = 1      
        await asyncio.sleep(0.1) # without this quart does not respon i.e. no monitoringd

    # producer.flush()


