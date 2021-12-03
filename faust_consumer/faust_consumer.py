import os
import time
import json
import faust
import mode
from aiohttp.web import Response
from aiologger import Logger

logger = Logger.with_default_handlers(name='my-logger')

health_status_timestamp = 0

# Using Call would be more elegant, but does not work with all the consumers
#class Call(faust.Record):
#    called_phone_number: str
#    start_call_epoch_time: int
#    call_duration: int

server_name = os.environ.get('BROKER_HOST_NAME', 'localhost')
server_port = os.environ.get('BROKER_HOST_PORT', '9092')
topic_name = os.environ.get('TOPIC', 'calls')
calls_threshold = os.environ.get('CALLS_THRESHOLD', 60)

app = faust.App('faust-consumer-agent', \
    agent_supervisor = mode.CrashingSupervisor, \
    worker_redirect_stdouts_level = 0, \
    broker='kafka://{}:{}'.format(server_name, server_port))


topic = app.topic(topic_name)

# event_table = app.GlobalTable('consumer_event_table', partitions=1)        

event_table = {}

@app.agent(topic)
async def adding(stream_call):
    try:
        
        async for message in stream_call:
            message = message if not isinstance(message, str) else json.loads(message)
            if 'value' in message:
                call_duration = message['value']['call_duration']
            else:
                call_duration = message['call_duration']
                
            global event_table
            if not 'calls_duration' in event_table:
                event_table['calls_duration'] = call_duration
            else:
                event_table['calls_duration'] = event_table['calls_duration']  + call_duration
            
            if not 'calls_number' in event_table:
                event_table['calls_number'] = 1
            else:
                event_table['calls_number'] = event_table['calls_number']  + 1
            
            global health_status_timestamp
            health_status_timestamp = int(time.time()) 
            
            if int(call_duration) > calls_threshold:
                logger.info(f'*********** LONG CALL: {message}')
    except Exception as e:
        logger.info(f'There was a problem with the topic {topic_name} stream, error= {e}')

@app.page('/metrics')
async def index(self, request):
    d = """
        <html>
        <body>
            <script>
                var evtSource = new EventSource("/");
                evtSource.onmessage = function(e) {
                    document.getElementById('response').innerText = e.data
                }
            </script>
            <div id="response"></div>
        </body>
    </html>
    """
    if 'calls_duration' not in event_table:
        calls_duration = 0
    else:
        calls_duration = event_table['calls_duration']
    if 'calls_number' not in event_table:
        calls_number = 0
    else:
        calls_number = event_table['calls_number']
        
    calls_duration_text = 'calls_duration {}\n'.format(str(calls_duration))
    calls_number_text = 'calls_number {}\n'.format(str(calls_number))
    
    if int(time.time()) - health_status_timestamp < 120:
        health_status = 'health_status 1\n'
    else:
        health_status = 'health_status 0\n'    
     
    response_text = ''.join([calls_duration_text, calls_number_text, health_status])
    return Response(text=response_text, content_type='text/html')
