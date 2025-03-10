import asyncio
import tornado.ioloop

async def my_task():
    print("Task running")
    await asyncio.sleep(1)
    print("Task completed")

async def main():
    asyncio.create_task(my_task())  # Create task
    await asyncio.sleep(2)  # Allow time for it to run

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())  # Force default policy
    tornado.ioloop.IOLoop.current().run_sync(main)  # Run with Tornado
