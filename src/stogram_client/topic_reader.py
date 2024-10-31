
from stogram_client.client import Client 
import asyncio 
import json
import time 

async def read_topics(topics):
    events_received = {}
    async with Client(host="127.0.0.1",port=8889) as client:
        await asyncio.gather(*[client.subscribe(t) for t in topics])
        time_start = time.time()
        async for obj in client:
            #print("\033[H\033[J",end="")
            print(obj)
            topic = None
            obj = None
            #if not obj:
            #    await asyncio.sleep(1)
            #    continue
            try:
                topic = obj['rows'][0][6]
                obj = json.loads(obj['rows'][0][len(obj['rows'][0])-1])
            except Exception as ex:
                print(ex)
                print(obj)
                continue
            if topic not in events_received:
                events_received[topic] = 0
            events_received[topic] += 1
            print(json.dumps(obj,indent=1))
            print(json.dumps(events_received,indent=1))
            print("Execution time: ",time.time() - time_start)


async def main():
    topics = ["test","debug","chat"]
    await read_topics(topics)

def cli():
    asyncio.run(main())   

if __name__ == '__main__':
    cli()
