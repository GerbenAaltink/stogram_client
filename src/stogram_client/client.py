from stogram_client import rlib
import asyncio
import json

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
        self.data = b''
        self.conncted = False
        self.semaphore = asyncio.Semaphore(1)

    async def add_event_handler(self,handler):
        self.event_handler = handler 
        return None
        if self.service is None:
            self.service = asyncio.create_task(self.run())

    async def execute(self,query,params=[]):
        return await self.call(dict(
            event="execute",
            query=query,
            params=params
        ))

    async def run(self):
        await self.connect()
        async for obj in self:
            if self.event_handler is not None:
                await self.event_handler(obj)

    async def call(self, obj):
        if hasattr(obj,'encode'):
            obj = obj.decode('utf-8')
        async with self.semaphore:
            await self.write(obj)
            result = await self.read())
            return result

    async def authenticate(self):
        print("Authenticating")
        return await self.call(dict(
            subscriber=self.name,
            event="register"
        ))

    async def close(self):
        if self.connected:
            self.connected = False  
            await self.writer.close()
    
    async def __aenter__(self):
        if not self.reader:
            await self.connect()
            self.connected = True 
        return self

    async def __aexit__(self,*args,**kwargs):
        pass
        #await self.close()
        
    async def connect(self):
        if not self.reader:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            await self.authenticate()
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
        while True:
            self.data += await self.reader.read(4096)
            
            length = rlib.json_length(self.data)
            if length:
                obj = json.loads(self.data[:length])
                self.data = self.data[length + 2:]
                yield obj


