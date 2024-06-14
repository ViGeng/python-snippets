'''
please wirte a simple python script to show me how to meet the requirements:
1. a single program running 2 threads
2. each thread running an event loop which running 2 tasks(routines)
3. routine1 is a websocket server and routine2 is a websocket sneder
4. with detailed comments and make the code modular
'''

import asyncio
import threading

import websockets

# Constants for WebSocket server and client
SERVER_HOST = "ws://localhost"

# WebSocket Server Routine
async def start_server(thread_id):
    async def handler(websocket, path):
        while True:
            try:
                message = await websocket.recv()
                print(f"Thread[{thread_id}-Received from client: {message}")
                await websocket.send(f"Echo: {message}")
            except websockets.ConnectionClosed:
                print(f"Thread[{thread_id}-Client disconnected")
                break
    async with websockets.serve(handler, "localhost", 12345+thread_id):
        await asyncio.Future()  # Run forever

# WebSocket Client Routine
async def websocket_sender(thread_id):
    await asyncio.sleep(1)  # Wait for server to start
    uri = f"{SERVER_HOST}:{12345+thread_id}"
    async with websockets.connect(uri) as websocket:
        for i in range(10):
            message = f"Thread[{thread_id}-Hello {i}"
            await websocket.send(message)
            print(f"Thread[{thread_id}-Sent to server: {message}")
            response = await websocket.recv()
            print(f"Thread[{thread_id}-Received from server: {response}")
            await asyncio.sleep(2)  # Simulate some work

async def hard_work():
    for i in range(10):
        print("Working hard")
        await asyncio.sleep(1)
        print("Hard work done")

# Thread Worker
def thread_worker(thread_id):
    routines = [
        start_server(thread_id),
        websocket_sender(thread_id),
        hard_work(),
    ]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(*routines))

if __name__ == "__main__":
    thread1 = threading.Thread(target=thread_worker, args=(1,))
    thread2 = threading.Thread(target=thread_worker, args=(2,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
