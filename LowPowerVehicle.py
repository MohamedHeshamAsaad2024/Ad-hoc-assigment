import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine IP address
host = "192.168.69.70"
port = 12001

# Connect to the server
client_socket.connect((host, port))

# The request to be sent to the HPV [Source, Destination]
source = 'B'
destination = 'A'
message = source + destination

# Send the request to the HPV
client_socket.sendall(message.encode('utf-8'))

# Receive a response from the server
response = client_socket.recv(1024).decode('utf-8')

# Format and print the path with arrows
formatted_path = " -> ".join(response)
print(f"Here is the shortest path: {formatted_path}")

# Close the connection
client_socket.close()