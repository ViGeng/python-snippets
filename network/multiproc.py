import asyncio
import multiprocessing

import websockets

HOST = "localhost"
PORT = 8765

async def echo(websocket, path):
    async for message in websocket:
        print(f"Server Received: {message}")
        await hard_work()
        await websocket.send(message)

async def server():
    server = await websockets.serve(echo, HOST, PORT)
    await server.wait_closed()

async def hard_work():
    for i in range(1000):
        print("Working hard")
        print("Hard work done")

async def client():
    uri = f"ws://{HOST}:{PORT}"
    await asyncio.sleep(1)

    async def send_data(websocket):
        for i in range(100):
            await hard_work()
            await websocket.send(f"Hello, server! = {i}")

    async def receive_ack(websocket):
        while True:
            response = await websocket.recv()
            print(f"Client Received: {response}")

    async with websockets.connect(uri) as websocket:
        send_task = asyncio.create_task(send_data(websocket))
        receive_task = asyncio.create_task(receive_ack(websocket))
        await asyncio.gather(send_task, receive_task)

def run_server():
    asyncio.run(server())

def run_client():
    asyncio.run(client())

if __name__ == "__main__":
    # Create server and client processes
    server_process = multiprocessing.Process(target=run_server)
    client_process = multiprocessing.Process(target=run_client)

    # Start server and client processes
    server_process.start()
    client_process.start()

    # Wait for server and client processes to finish
    server_process.join()
    client_process.join()