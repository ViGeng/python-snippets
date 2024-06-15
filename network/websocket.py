import asyncio

import websockets


async def echo(websocket, path):
    async for message in websocket:
        print(f"Server Received: {message}")
        await websocket.send(message)


async def server():
    start_server = websockets.serve(echo, "localhost", 8765)
    await start_server


async def client():
    uri = "ws://localhost:8765"
    await asyncio.sleep(1)
    async with websockets.connect(uri) as websocket:
        for i in range(3):
            await asyncio.sleep(1)
            await websocket.send("Hello, server!")
            response = await websocket.recv()
            print(f"Client Received: {response}")


async def main():
    # Run the server
    await server()

    # Run the client
    await client()

if __name__ == "__main__":
    asyncio.run(main())

