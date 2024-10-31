import asyncio 
from stogram_client import Client
from stogram_client.topic_reader import read_topics 

async def publish(times):
    client = Client()
    async with Client() as client:
        tasks = []
        for x in range(times):
            tasks.append(client.publish("debug",dict(message_nr=x)))
            tasks.append(client.publish("test",dict(message_nr=x)))
        await asyncio.gather(*tasks)
  



async def bench(times,read=False):
    topics = ['chat','debug','test']
    tasks = []
    if read:
        tasks.append(asyncio.create_task(read_topics(topics)))
    tasks.append(asyncio.create_task(publish(times)))
    await asyncio.gather(*tasks)

def main():
    import sys
    times = 0
    try:
        times = int(sys.argv[1])
    except:
        pass

    if not times:
        times = 10000

    read = '--read' in sys.argv
    print("Testing",times,"times.")
    asyncio.run(bench(times,read))

if __name__ == '__main__':
    main()

