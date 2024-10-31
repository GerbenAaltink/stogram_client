from stogram_client import rlib
import asyncio
import json
import uuid

class Client:
    def __init__(self, name=None, host="127.0.0.1", port=8889):
        self.host = host 
        self.port = port 
        self.name = name or str(uuid.uuid4())
        self.reader = None 
        self.writer = None 
        self.authenticated = False 
        self.event_handler = None
        self.service = None
        self.data = b''
        self.connected = False
        self.semaphore = asyncio.Semaphore(1)
        self.context_semaphore = asyncio.Semaphore(11)
        self.read_semaphore = asyncio.Semaphore(11)

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
            result = await asyncio.gather(self.write(obj),self.read())
        return result[0]

    async def authenticate(self):
        return await self.call(dict(
            subscriber=self.name,
            event="register"
        ))

    def close(self):
        if self.connected:
            self.connected = False  
            self.writer.close()
    
    async def __aenter__(self):
        await self.context_semaphore.acquire()
        if not self.reader:
            await self.connect()
            self.connected = True 
        return self

    async def __aexit__(self,*args,**kwargs):
        self.close()
        self.context_semaphore.release()
        
        
    async def connect(self):
        if not self.connected:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected  = True
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
        result = None 
        async for obj in self:
            result = obj
            break 
        return result  

    async def __aiter__(self):
        #async with self.read_semaphore:
        while True:
            chunk = await self.reader.read(4096)
            if not chunk:
                break
            self.data += chunk
            #while self.data[0] in ["\r".encode('utf-8'),"\n".encode('utf-8')]:
            #    self.data = self.data[1:]
           # print(self.data)
            length = rlib.json_length(self.data)
            if length:
                
                self.data = self.data[length+2:]
                
                print(self.data)
                obj = json.loads(self.data[:length])


                yield obj


