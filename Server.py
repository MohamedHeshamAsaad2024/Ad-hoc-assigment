import socket

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine IP address
host = socket.gethostbyname(socket.gethostname())
port = 12345

# Bind to the port
server_socket.bind((host, port))

# Queue up to 5 requests
server_socket.listen(5)

print(f"Server is listening on {host}:{port}")

while True:
    # Establish a connection
    client_socket, addr = server_socket.accept()
    print(f"Got a connection from {addr}")

    message = client_socket.recv(1024).decode('utf-8')
    print(f"Received message: {message}")
    
    #Eslam responsibility
    # Asking cloud to get all possible paths from 
    print(f"Asking for cloud for best path ")

    # Send a response back to the client
    response = "The best path is from A to B "
    client_socket.send(response.encode('utf-8'))

    # Close the connection
    client_socket.close()