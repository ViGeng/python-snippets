import asyncio
import multiprocessing
import time

import websockets

'''
   Process1                                        
  ┌──────────────────────────┐                     
  │  Thread1                 │                     
  │ ┌──────────────────────┐ │                     
  │ │  routine1            │ │                     
  │ │ ┌─────────────────┐  │ │                     
  │ │ │task-send_data   │  │ │                     
  │ │ └─────────────────┘  │ │              CPU0   
  │ │  routine2            │ │                     
  │ │ ┌─────────────────┐  │ │                     
  │ │ │task-receive_ack │  │ │                     
  │ │ └─────────────────┘  │ │                     
  │ │                      │ │                     
  │ └──────────────────────┘ │                     
  │                          │                     
  └──────────────────────────┘                     
                                                   
   Process2                                        
  ┌──────────────────────────┐                     
  │  Thread1                 │                     
  │ ┌─────────────────────┐  │                     
  │ │                     │  │                     
  │ │ ┌────────────────┐  │  │                     
  │ │ │task-server     │  │  │                     
  │ │ └────────────────┘  │  │                     
  │ │                     │  │                     
  │ └─────────────────────┘  │                     
  │  Thread2                 │              CPU1   
  │ ┌─────────────────────┐  │                     
  │ │  routine1           │  │                     
  │ │ ┌────────────────┐  │  │                     
  │ │ │task-send_result│  │  │                     
  │ │ └────────────────┘  │  │                     
  │ │                     │  │                     
  │ └─────────────────────┘  │                     
  │                          │                     
  └──────────────────────────┘                     
   Process3                                        
  ┌──────────────────────────┐                     
  │  Thread3                 │                     
  │ ┌─────────────────────┐  │                     
  │ │  routine1           │  │                     
  │ │ ┌────────────────┐  │  │                     
  │ │ │task-worker_proc│  │  │             CPU2    
  │ │ └────────────────┘  │  │                     
  │ │                     │  │                     
  │ └─────────────────────┘  │                     
  │                          │                     
  └──────────────────────────┘                     
'''



HOST = "localhost"
PORT = 8765

q = multiprocessing.Queue()
rstq = multiprocessing.Queue()

def hard_work(load=5):
    for i in range(load):
        for _ in range(10000000):
            a = 99999 * 99999

# Worker Process
def worker_process():
    while True:
        task = q.get()
        time.sleep(1)  # Simulate work
        hard_work()
        rstq.put(f"Hard work {task} done")

def send_results(websocket):
    while True:
        result = rstq.get()
        asyncio.run(websocket.send(result))

# Server Process
def server_process():
    import threading
    async def echo(websocket, path):
        # Start the send_results function in a separate thread for this connection
        send_results_thread = threading.Thread(target=send_results, args=(websocket,))
        send_results_thread.start()

        # Handle incoming messages
        async for message in websocket:
            print(f"Server Received: {message}")
            q.put(message)

        # When the connection is closed, stop the send_results thread
        send_results_thread.join()

    async def server():
        server = await websockets.serve(echo, HOST, PORT)
        await server.wait_closed()

    asyncio.run(server())

async def client():
    uri = f"ws://{HOST}:{PORT}"
    await asyncio.sleep(1)

    async def send_data(websocket):
        for i in range(100):
            await asyncio.sleep(1)
            await websocket.send(f"Hello, server! = {i}")

    async def receive_ack(websocket):
        while True:
            response = await websocket.recv()
            print(f"Client Received: {response}")

    async with websockets.connect(uri) as websocket:
        send_task = asyncio.create_task(send_data(websocket))
        receive_task = asyncio.create_task(receive_ack(websocket))
        await asyncio.gather(send_task, receive_task)

def run_client():
    asyncio.run(client())

if __name__ == "__main__":

    # Create server, client, and worker processes
    server_process = multiprocessing.Process(target=server_process)
    client_process = multiprocessing.Process(target=run_client)
    worker_process = multiprocessing.Process(target=worker_process)

    # Start server, client, and worker processes
    server_process.start()
    client_process.start()
    worker_process.start()

    # Wait for server, client, and worker processes to finish
    server_process.join()
    client_process.join()
    worker_process.join()