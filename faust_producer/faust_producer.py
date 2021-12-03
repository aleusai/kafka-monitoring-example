import os
import time
from json import dumps
import faust
import mode
from aiohttp.web import Response
from message_builder import get_calls_info
import asyncio

health_status_timestamp = 0

#class Call(faust.Record):
#    called_phone_number: str
#    start_call_epoch_time: int
#    call_duration: int
#    #value: dict
#    key: bytes

server_name = os.environ.get('BROKER_HOST_NAME', 'localhost')
server_port = os.environ.get('BROKER_HOST_PORT', '9092')
topic_name = os.environ.get('TOPIC', 'calls')

app = faust.App('faust-producer-agent', agent_supervisor = mode.CrashingSupervisor, \
    broker='kafka://{}:{}'.format(server_name, server_port))

topic = app.topic(topic_name)
    
@app.timer(1)
async def my_timer_function():
    messages_list = get_calls_info()
    #for message in messages_list:
    #    await send_message.send(value=message)
    await send_message.send(value=messages_list)
    await asyncio.sleep(0.1)

    
@app.agent()
async def send_message(stream_from_timer_func):
        async for messages_list in stream_from_timer_func:
            try:
                for message in messages_list:
                    print('****** producer message= ', message)
                    called_phone_number = message['value']['called_phone_number']
                    start_call_epoch_time = message['value']['start_call_epoch_time']
                    call_duration = message['value']['call_duration']
                    caller_number = message['key']
                    value = {'key': caller_number,'called_phone_number': called_phone_number, 
                                    'start_call_epoch_time': start_call_epoch_time,
                                    'call_duration': call_duration}
                    await topic.send(
                        value=dumps(value)
                    )  
                    global health_status_timestamp
                    health_status_timestamp = int(time.time())                 
            except Exception as e:
                print('Exception {} occurred'.format(e))
                
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

    if int(time.time()) - health_status_timestamp < 120:
        health_status = 'health_status 1\n'
    else:
        health_status = 'health_status 0\n'  
    return Response(text=health_status, content_type='text/html')
