import socket
import threading
import time
import random
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))  # Use localhost and port 12345
server.listen(5)
print("Server is listening on port 12345...")

file_lock = threading.Lock()

def handle_client(client_socket):
    while True:
        try:
            # Receive a command from the client
            message = client_socket.recv(1024).decode()

            if message.startswith("write:"):
                # Call a function to handle write operation and pass the data
                data_to_write = message.split(":", 1)[1]  # Extract data after "write:"
                handle_write(client_socket, data_to_write)
            elif message == "read":
                # Call a function to handle read operation
                handle_read(client_socket)
            else:
                print("Unknown command received:", message)
        except Exception as e:
            print(f"Error handling client: {e}")
            break

    client_socket.close()

def handle_read(client_socket):
    # Lock the file to prevent conflicts
    with file_lock:
        time.sleep(random.randint(1, 7))  # Random delay
        with open('data.json', 'r') as file:
            data = json.load(file)
            client_socket.send(str(data).encode())

def handle_write(client_socket, data_to_write):
    with file_lock:
        time.sleep(random.randint(1, 7))  # Random delay
        # Write the received data into the file
        with open('data.json', 'w') as file:
            json_data = {"message": data_to_write}  # Use the data sent from the client
            json.dump(json_data, file)
            client_socket.send("Write successful".encode())

while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
