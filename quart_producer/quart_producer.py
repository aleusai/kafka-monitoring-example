import asyncio
from quart import Quart
from kafka_prod import kafka_producer
from health_status import health_status


loop = asyncio.get_event_loop()
loop.create_task(kafka_producer())

      
app = Quart(__name__)  

@app.route("/metrics")
async def notify():
    return f"health_status {health_status}\n"
    
if __name__ == "__main__":
    app.run(debug=False,loop=loop, host='0.0.0.0')
