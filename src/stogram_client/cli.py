import argparse
import asyncio 
import json 
from stogram_client.client import Client




async def test():
    
    client = Client()
    await client.add_event_handler(lambda x: print(x))
    print(await client.connect())
    print(await client.authenticate())
    tasks = []
    for x in range(500):
        tasks.append(client.publish("debug",dict(message_nr=x)))
        tasks.append(client.publish("test",dict(message_nr=x)))
       
    await asyncio.gather(*tasks)
  


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str,default="localhost")
    parser.add_argument("--port", type=int,default=8889)
    args = parser.parse_args()
    print("Connecting to {}:{}".format(args.host,args.port))
    asyncio.run(test())
