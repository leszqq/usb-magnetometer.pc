import asyncio
import time
from asyncio import shield


# a blocking io-bound task
def blocking_task():
    # report a message
    print('Task starting')
    # block for a while
    time.sleep(2)
    # report a message
    print('Task done')


async def test_task():
    await asyncio.sleep(1)
    print('t1 done')


# main coroutine
async def main():
    print('Main running the blocking task')
    task = asyncio.create_task(asyncio.to_thread(blocking_task))
    #t1 = asyncio.create_task(test_task())
    print('Main doing other things')
    # allow the scheduled task to start

    while True:
        try:
            await asyncio.wait_for(shield(task), timeout=0.3)
            break
        except asyncio.exceptions.TimeoutError:
            print("Not done yet...")

    print('done')



# run the asyncio program
asyncio.run(main())
