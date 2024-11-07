import socket
import threading
import time
import random
import json

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 12345))
server.listen(5)
print("Server is listening on port 12345...")

# Synchronization primitives
file_lock = threading.Lock()
write_complete = threading.Condition(file_lock)
active_writes = 0  # Counter to track active write operations


def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message.startswith("write:"):
                data_to_write = message.split(":", 1)[1]
                handle_write(client_socket, data_to_write)
            elif message == "read":
                handle_read(client_socket)
            else:
                print("Unknown command received:", message)
        except Exception as e:
            print(f"Error handling client: {e}")
            break

    client_socket.close()


def handle_write(client_socket, data_to_write):
    global active_writes
    with write_complete:  # Lock acquired here
        active_writes += 1  # Indicate a write operation is in progress

    time.sleep(random.randint(1, 7))  # Simulate processing time

    # Perform the write operation
    with file_lock:
        with open('data.json', 'w') as file:
            json_data = {"message": data_to_write}
            json.dump(json_data, file)
            client_socket.send("Write successful".encode())

    with write_complete:
        active_writes -= 1  # Decrement active writes count
        if active_writes == 0:
            write_complete.notify_all()  # Notify waiting read threads that writing is done


def handle_read(client_socket):
    with write_complete:  # Acquire lock for coordination
        while active_writes > 0:  # Wait if there are active write operations
            write_complete.wait()

        # No active writes, it's safe to read
        time.sleep(random.randint(1, 7))  # Simulate processing time
        with open('data.json', 'r') as file:
            data = json.load(file)
            client_socket.send(str(data).encode())


while True:
    client_socket, addr = server.accept()
    print(f"Accepted connection from {addr}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
