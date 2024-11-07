import socket

def write_test(custom_message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    # Send write command with custom data
    message = f"write:{custom_message}"
    client.send(message.encode())  # Send write command to the server with data
    response = client.recv(1024).decode()  # Receive the server response
    print(f"Server response: {response}")
    client.close()

if __name__ == "__main__":
    # You can ask for custom data here, for example:
    custom_data = input("Enter the data to write to the file: ")
    write_test(custom_data)
