import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine IP address
host = "192.168.1.24"
port = 12345

# Connect to the server
client_socket.connect((host, port))

# Send a message to the server
message = "Need to know shortest path to move from Zayed to Eltagmoa"
client_socket.send(message.encode('utf-8'))

# Receive a response from the server
response = client_socket.recv(1024).decode('utf-8')
print(f"Here is the shortest path: {response}")

# Close the connection
client_socket.close()