

from stogram_client.client import Client 
import asyncio 
import json
import time 
import random 

async def read_topics(topics, host="127.0.0.1",port=9000,name=None):
    events_received = {}
    port = 7001
    async with Client(host="127.0.0.1",port=port,name=name) as client:
        await asyncio.gather(*[client.subscribe(t) for t in topics])
        time_start = time.time()
        async for obj in client:
            topic = None
            try:
                if len(obj['columns']) == 7 and obj['columns'][6] == 'topic':
                    topic = obj['rows'][0][6]
                    obj = json.loads(obj['rows'][0][7])
            except Exception as ex:
                pass
            if topic not in events_received:
                events_received[topic] = 0
            events_received[topic] += 1
            print(json.dumps(obj,indent=1))
            print(json.dumps(events_received,indent=1))
            print("Name: %s",client.name);
            print("Execution time on port {}:{}".format(port,time.time() - time_start))


async def main():
    topics = ["test","debug","chat"]
    await read_topics(topics, port=7001, name="debug_client")

def cli():
    asyncio.run(main())   

if __name__ == '__main__':
    cli()
