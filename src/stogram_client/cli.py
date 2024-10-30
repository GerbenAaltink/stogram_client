import argparse
import asyncio 
import json 
from stogram_client import rlib

class Client:
    def __init__(self, name="stogram", host="127.0.0.1", port=8889):
        self.host = host 
        self.port = port 
        self.name = name 
        self.reader = None 
        self.writer = None 
        self.authenticated = False 
        self.event_handler = None
        self.service = None
        self.semaphore = asyncio.Semaphore(1)

    async def add_event_handler(self,handler):
        self.event_handler = handler 
        return None
        if self.service is None:
            self.service = asyncio.create_task(self.run())

    async def run(self):
        await self.connect()
        async for obj in self:
            if self.event_handler is not None:
                await self.event_handler(obj)

    async def call(self, obj):
        if hasattr(obj,'encode'):
            obj = obj.decode('utf-8')
        async with self.semaphore:
            result = await asyncio.gather(self.write(obj),self.read())
        print(result)
        return result[1]

    async def authenticate(self):
        print("Authenticating")
        return await self.call(dict(
            subscriber=self.name,
            event="register"
        ))
    


    async def connect(self):
        if not self.reader:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def write(self,obj):
        string = json.dumps(obj)
        self.writer.write(string.encode())
        await self.writer.drain()

    async def publish(self, topic, data):
        return await self.call(dict(
            event="publish",
            topic=topic,
            message=json.dumps(data,default=str)
        ))

    async def subscribe(self, topic):
        if type(topic) == list:
            tasks = []
            for t in topic:
                tasks.append(self.subscribe(t))
            return await asyncio.gather(*tasks)
            
        await self.call(dict(
            subscriber=self.name,
            event="subscribe",
            topic=topic
        ))

    async def read(self):
        async for obj in self:
            return obj 

    async def __aiter__(self):
        data = b''
        while True:
            data += await self.reader.read(4096)
            length = rlib.json_length(data)
            if length:
                obj = json.loads(data[:length])
                data = data[length:]
                yield obj







async def test():
    
    client = Client()
    await client.add_event_handler(lambda x: print(x))
    print(await client.connect())
    print(await client.authenticate())
    tasks = []
    for x in range(500):
        tasks.append(client.publish("test",dict(message_nr=x)))
        tasks.append(client.subscribe("test"))
    tasks.append(client.subscribe("test"))
    await asyncio.gather(*tasks)
    await client.authenticate()
    await client.authenticate()
    await client.authenticate()
  


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str,default="localhost")
    parser.add_argument("--port", type=int,default=8889)
    args = parser.parse_args()
    print("Connecting to {}:{}".format(args.host,args.port))
    asyncio.run(test())
