import socket


def read_test():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send("read".encode())  # Send read command to the server
    response = client.recv(1024).decode()  # Receive the server response
    print(f"Server response: {response}")
    client.close()


if __name__ == "__main__":
    read_test()
