from stogram_client import rlib
import asyncio
import json
import uuid
import socket

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
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
        self.connected_sync = False

    async def add_event_handler(self,handler):
        self.event_handler = handler 
        return None
        if self.service is None:
            self.service = asyncio.create_task(self.run())

    async def execute(self,query,params=[]):
        return await self.call_async(dict(
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
        if self.connected:
        
            if hasattr(obj,'encode'):
                obj = obj.decode('utf-8')
            async with self.semaphore:
                await self.write(obj)
                result = await self.read()
                return result
        else:
            return await call_sync(self,obj)


    async def authenticate(self):
        return await self.call(dict(
            subscriber=self.name,
            event="register"
        ))

    async def authenticate_sync(self):
        return await self.call_sync(dict(
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
        return await self.call_sync(dict(
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

    async def call_sync(self, data):
        if not self.connected_sync:
            self.socket.connect((self.host,self.port))
            self.connected_sync = True
            await self.authenticate_sync()
        data = json.dumps(data)
        self.socket.sendall(data.encode('utf-8'))
        data = b''
        while True:
            chunk = self.socket.recv(4096)
            if not chunk:
                break
            data += chunk
            
            if data.startswith(b'\r\n'):
                data = data[2:]
           
            #print(self.data)

            length = rlib.json_length(data)

            if length:
                obj = json.loads(data[:length])
                data = data[length:]
                
                if data.endswith(b'\r\n'):
                    data = data[2:]
     
                return obj 


    async def __aiter__(self):
        #async with self.read_semaphore:
        while True:
            chunk = await self.reader.read(4096)
            

            if not chunk:
                break
            self.data += chunk
            

            
            if self.data.startswith(b'\r\n'):
                self.data = self.data[2:]
           
            #print(self.data)

            length = rlib.json_length(self.data)

            if length:
                obj = json.loads(self.data[:length])
                self.data = self.data[length:]
                
                if self.data.endswith(b'\r\n'):
                    self.data = self.data[2:]
     
                yield obj


