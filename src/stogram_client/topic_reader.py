
from stogram_client.client import Client 
import asyncio 

async def read_topics(topics):

    async with Client(host="127.0.0.1",port=8889) as client:
        await asyncio.gather(*[client.subscribe(t) for t in topics])

        async for obj in client:
            print(obj)


async def main():
    topics = ["test","debug","chat"]
    await read_topics(topics)

def cli():
    asyncio.run(main())   

if __name__ == '__main__':
    cli()