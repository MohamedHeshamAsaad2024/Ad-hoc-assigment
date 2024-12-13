#############################################################################
# File: CloudServer.py
# Description: This file implements the Cloud Server for the AdHocVcc 
#              network. It maintains a graph representing the network 
#              topology and edge weights, and provides these weights to 
#              High-Power Vehicles (HPVs) upon request.  The server uses TCP 
#              sockets for communication and pickle for data serialization.
#############################################################################
#############################################################################
#                              I N C L U D E S                              #
#############################################################################
import socket
import pickle

#############################################################################
#                               G L O B A L S                               #
#############################################################################
# Global graph such that each node is represented by a character 'A', 'B', ..etc. and each path has an integer weight
CloudServer_GlobalGraph = {
    ('A', 'D'): 1,
    ('A', 'B'): 6,
    ('D', 'B'): 2,
    ('D', 'E'): 1,
    ('E', 'B'): 2,
    ('E', 'C'): 5,
    ('B', 'C'): 5
}

#############################################################################
#                             F U N C T I O N S                             #
#############################################################################
#############################################################################
# Function: CloudServer_Init
# Description:  Creates a TCP socket, binds it to the host's IP address and 
#               a specified port, and sets it to listen for incoming 
#               connections.
# Args: None
# Returns:
#    socket.socket: The initialized server socket object.
#############################################################################
def CloudServer_Init():
    # Creat a socket using IPv4 and TCP
    cloudServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set the IP address to be the IP address of the current host
    host = socket.gethostbyname(socket.gethostname())

    # The port through which the Cloud Server will provide its service
    port = 12000

    # Bind the socket to the IP address and the port number defined
    cloudServerSocket.bind((host, port))

    # Define a pool of one client to be served at the time
    cloudServerSocket.listen(1)

    # Print a message indicating successful server initializtion
    print(f"Server is initialized and listening on {host}:{port}")

    # Return the cloud server socket
    return cloudServerSocket

#############################################################################
# Function: CloudServer_WaitForConnection
# Description: Waits for a client connection on the provided server socket, 
#              performs a connectivity test by exchanging a test message, and
#              returns the client socket and address upon successful connection.
# Args:
#    serverSocket (socket.socket): The server socket object to listen on.
# Returns:
#    tuple: A tuple containing the client socket and client address if the
#           connection and connectivity test are successful. Returns (None, None)
#           if an error occurs during connection or the connectivity test.
#############################################################################
def CloudServer_WaitForConnection(serverSocket):
    # Wait for a client to connect to the server
    clientSocket, clientAddress = serverSocket.accept()

    # Print the address of the client connected
    print(f"Received a connection from {clientAddress}")

    try:
        # Print a message to indicate testing of connectivity
        print(f"Testing Connectivity ...")

        # Wait for a test message to be received to confirm connectivity
        testMessage = clientSocket.recv(1024).decode('utf-8')

        # Send back the test message for mutual confirmation of connectivity
        clientSocket.send(testMessage.encode('utf-8'))

        # Print a message to indicate testing of connectivity
        print(f"Connectivity testing completed successfully")

        # Return if test message received and sent successfully
        return clientSocket, clientAddress
    
    except (socket.timeout, socket.error, OSError) as e:

        # Print an error message indicating connection testing failure
        print(f"Connectivity testing failed with the following error: {e.strerror}")

        # Return None to indicate failure
        return None, None  

#############################################################################
# Function: CloudServer_SendWeights
# Description: Serializes and sends the graph weights (CloudServer_GlobalGraph) 
#              to the specified target socket.
# Args:
#    targetSocket (socket.socket): The socket to send the weights to.
#    targetAddress (tuple): The address of the target (IP, port).  Used for 
#                           informational messages only.
# Returns: None
#############################################################################
def CloudServer_SendWeights(targetSocket, targetAddress):
    # Print a message indicating the beginning of serialized data transmission
    print(f"Sending the weights of all possible paths to the requesting node {targetAddress}")

    # Serialize the array using pickle
    serializedWights = pickle.dumps(CloudServer_GlobalGraph)

    try:
        # Send the serialized data to the target address
        targetSocket.sendall(serializedWights)
        print("Weights sent successfully")

    except (socket.error, BrokenPipeError) as e:
        # In case of failure during transmission, print the failure
        print(f"Error sending weights: {e.strerror}")

    return

#############################################################################
#                                  M A I N                                  #
#############################################################################
#############################################################################
# Function: main
# Description: Initializes the Cloud Server, listens for incoming connections,
#              and sends the graph weights (CloudServer_GlobalGraph) to 
#              connected clients.  Runs continuously until manually stopped.
# Args: None
# Returns: None
#############################################################################
def main():
    # Initialize the cloud server socket
    serverSocket = CloudServer_Init()

    # Run the server continously
    while True:
        # Wait for a node to request the weights of the paths monitored
        clientSocket, clientAddress = CloudServer_WaitForConnection(serverSocket)

        # If the connection status is successful
        if clientSocket is not None:
            # Send the weights of the paths
            CloudServer_SendWeights(clientSocket, clientAddress)

        # Close the connection
        clientSocket.close()

if __name__ == "__main__":
    main()