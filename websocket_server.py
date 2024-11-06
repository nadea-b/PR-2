import asyncio
import websockets

# In-memory storage for users and their connections
connected_users = {}

async def chat_handler(websocket, path):
    username = None
    try:
        # Wait for user to join the chat room (send their name)
        while True:
            message = await websocket.recv()
            if message.startswith("join_room:"):
                username = message[len("join_room:"):].strip()
                connected_users[username] = websocket
                print(f"{username} has joined the chat.")
                # Notify everyone that the user has joined
                for user, conn in connected_users.items():
                    if user != username:
                        await conn.send(f"{username} has joined the chat.")
                await websocket.send(f"Welcome {username}!")  # Send a welcome message
                break

        # Broadcast messages to others in the chat room
        async for message in websocket:
            if message == "leave_room":
                # Remove user from connected users list
                connected_users.pop(username, None)
                # Notify everyone that the user has left
                for user, conn in connected_users.items():
                    await conn.send(f"{username} has left the chat.")
                break
            elif message.startswith("send_msg:"):
                # Send the message to all other users
                chat_message = message[len("send_msg:"):].strip()
                # Send message to all other users
                for user, conn in connected_users.items():
                    if user != username:  # Don't send to the sender
                        await conn.send(f"{username}: {chat_message}")
                # Send the message back to the sender
                await websocket.send(f"{username}: {chat_message}")
    except websockets.ConnectionClosed:
        print(f"Connection with {username} closed.")
        if username:
            connected_users.pop(username, None)

def start_websocket_server():
    # Start the WebSocket server
    server = websockets.serve(chat_handler, "localhost", 6789)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    start_websocket_server()
