from stogram_client.client import Client
import asyncio 
import readline 
import os 

class Database:
    def __init__(self,host="127.0.0.1", port=8889):
        self.name = None
        self.host = host 
        self.port = port 
        self.stogram = None 

    async def __aenter__(self):
        if not self.stogram:
            self.stogram = Client(name=self.name,host=self.host,port=self.port)
            await self.stogram.connect()
            await self.stogram.authenticate()
        return self 
    
    async def __aexit__(self, type, value, traceback):
        if self.stogram:
            self.stogram.close()

    async def execute(self,query,params=[]):
        return await self.stogram.execute(query,params=params)

    async def close(self):
        if self.stogram:
            await self.stogram.close()

async def main():

    path = os.path.expanduser("~/.stogram_db_client_history")
    if(os.path.exists(path)):
        readline.read_history_file(path)
    print("Stogram database client")
    async with Database() as db:
        
        while True:
            query = input("> ")
            if query == "exit":
                
                break

            readline.write_history_file(path)
            print(await db.execute(query))

def cli():
    asyncio.run(main())

if __name__ == '__main__':
    cli()
