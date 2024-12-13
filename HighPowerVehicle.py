#############################################################################
# File: HighPowerVehicle.py
# Description: This file implements the High-Power Vehicle (HPV) functionality 
#              for the AdHocVcc network.  The HPV acts as an intermediary 
#              between Low-Power Vehicles (LPVs) and the Cloud Server. It 
#              receives routing requests from LPVs, retrieves network 
#              topology information (weights) from the Cloud Server, calculates 
#              the shortest path using Dijkstra's algorithm, and sends the 
#              calculated path back to the requesting LPV.
#############################################################################
#############################################################################
#                              I N C L U D E S                              #
#############################################################################
import socket
import pickle
import heapq

#############################################################################
#                               G L O B A L S                               #
#############################################################################
# Cloud server information to connect to
HPV_CloudServerIpAddress = "192.168.69.70"
HPV_CloudServerPortNumber = 12000

# HPV Port Number to offer the service
HPV_PortNumber = 12001

#############################################################################
#                             F U N C T I O N S                             #
#############################################################################

#############################################################################
# Function: HPV_InitServer
# Description: Initializes the High-Power Vehicle (HPV) server socket. Creates a 
#              TCP socket, binds it to the host IP and a specified port, and 
#              starts listening for incoming connections.
# Args: None
# Returns:
#     socket.socket: The initialized HPV server socket.
#############################################################################
def HPV_InitServer():
    # Creat a socket using IPv4 and TCP
    HpvServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Set the IP address to be the IP address of the current host
    host = socket.gethostbyname(socket.gethostname())

    # Bind the socket to the IP address and the port number defined
    HpvServerSocket.bind((host, HPV_PortNumber))

    # Define a pool of one client to be served at the time
    HpvServerSocket.listen(1)

    # Print a message indicating successful server initializtion
    print(f"HPV Server is initialized and listening on {host}:{HPV_PortNumber}")

    # Return the cloud server socket
    return HpvServerSocket

#############################################################################
# Function: HPV_WaitForLpvSession
# Description: Accepts a connection from a Low-Power Vehicle (LPV) on the 
#              provided server socket.
# Args:
#     serverSocket (socket.socket): The server socket to listen on.
# Returns:
#     socket.socket: The client socket for the connected LPV.
#############################################################################
def HPV_WaitForLpvSession(serverSocket):
    # Wait for a client to connect to the server
    clientSocket, clientAddress = serverSocket.accept()

    # Print the address of the client connected
    print(f"Received a connection from {clientAddress}")

    return clientSocket

#############################################################################
# Function: HPV_ConnectToCloudServer
# Description: Establishes a connection to the Cloud Server and performs a 
#              connectivity test.
# Args: None
# Returns:
#     socket.socket: The client socket if the connection and connectivity test 
#                    are successful, None otherwise.
#############################################################################
def HPV_ConnectToCloudServer():
    # Creat a socket using IPv4 and TCP
    HpvclientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the cloud server
        HpvclientSocket.connect((HPV_CloudServerIpAddress, HPV_CloudServerPortNumber))

        # Print a message to indicate connection to the Cloud Server
        print(f"Connected to the Cloud Server at {HPV_CloudServerIpAddress}:{HPV_CloudServerPortNumber}")
        
        try:
            # Print a message to indicate testing of connectivity
            print(f"Testing Connectivity ...")

            # Define a test message for connectivity testing
            test_message = "Test connection"

            # Send the Message to the Cloud Server
            HpvclientSocket.send(test_message.encode('utf-8'))

            # Expect the same message to be received from the cloud server
            response = HpvclientSocket.recv(1024).decode('utf-8')

            # Check that both messages are similar
            if response == test_message:
                # If both are similar, print the successful connectivity
                print("Connectivity test successful")

                # Return True
                return HpvclientSocket
            else:
                # If both are notsimilar, print the failure in connectivity
                print(f"Connectivity test failed. Expected '{test_message}', got '{response}'")

                # Return False
                return None
            
        except (socket.timeout, socket.error, OSError) as e:
            # Print an error in case of connectivity test failure
            print(f"Error during connectivity test: {e.strerror}")

            # Return False
            return None
        
    except (socket.timeout, socket.error, OSError, ConnectionRefusedError) as e:
        # Print an error message indicating connection failure
        print(f"Error connecting to server: {e.strerror}")

        # Return False
        return None

#############################################################################
# Function: HPV_ReceiveLpvRequest
# Description: Receives and decodes the source and destination request from the
#              connected LPV.
# Args:
#     clientSocket (socket.socket): The socket connected to the LPV.
# Returns:
#     tuple: A tuple containing the source and destination characters. Returns
#           (None, None) if an error occurs or the received data is invalid.
#############################################################################
def HPV_ReceiveLpvRequest(clientSocket):
    try:
        # Receive data from the LPV. We expect 2 bytes.
        data = clientSocket.recv(2).decode('utf-8')

        # Check if we received enough data
        if len(data) != 2:
            print("Error: Invalid request received from LPV. Expected 2 bytes.")
            return None, None

        # Extract source and destination as characters
        source = data[0]
        destination = data[1]

        print(f"Received request from LPV: Source={source}, Destination={destination}")
        return source, destination

    except (socket.timeout, socket.error, OSError) as e:
        print(f"Error receiving request from LPV: {e.strerror}")
        return None, None

#############################################################################
# Function: HPV_ReceiveWeights
# Description: Receives and deserializes the graph weights from the Cloud Server.
# Args:
#     clientSocket (socket.socket): The socket connected to the Cloud Server.
# Returns:
#     dict: A dictionary containing the deserialized graph weights. Returns None
#           if an error occurs during reception or deserialization.
#############################################################################
def HPV_ReceiveWeights(clientSocket):
    try:
        # Receive the weights from the the Cloud Server
        serializedWeights = clientSocket.recv(1024)

        # Deserialize the weights into a byte array for processing
        pathsWeights = pickle.loads(serializedWeights)

        # Print the received weights
        print(f"Received weights: {pathsWeights}")

        # Return the received weights
        return pathsWeights
    
    except (pickle.UnpicklingError, socket.error, OSError) as e:
        # Print an error message in case of reception or deserialization error
        print(f"Error receiving or deserializing weights: {e.strerror}")

        # Return None
        return None

#############################################################################
# Function: HPV_SendShortestPath
# Description: Sends the calculated shortest path to the connected LPV.  If no 
#              path exists, sends an error code.
# Args:
#     clientSocket (socket.socket): The socket connected to the LPV.
#     shortestPath (list): A list of characters representing the shortest path,
#                         or None if no path exists.
# Returns: None
#############################################################################
def HPV_SendShortestPath(clientSocket, shortestPath):
    try:
        # Check if a path was found
        if shortestPath is None:
            # Send a special code (e.g., -1) to indicate no path found
            clientSocket.sendall(bytes([-1]))  # Example using a single byte
            print("No path found. Sending error code to LPV.")
            return
        
        # Convert list to string
        path_string = "".join(shortestPath)

        # Send combined length and data
        clientSocket.sendall(path_string.encode("utf-8"))
        print(f"Sent shortest path: {shortestPath} to LPV.")

    except (socket.timeout, socket.error, OSError, TypeError) as e:
        print(f"Error sending shortest path to LPV: {e}")

#############################################################################
# Function: HPV_GetShortestPath
# Description: Calculates the shortest path between two points in a graph 
#              using Dijkstra's algorithm. Considers bidirectional edges.
# Args:
#     source (str): The starting node.
#     destination (str): The destination node.
#     map (dict): The graph represented as a dictionary of weighted edges.
#                 Keys are tuples (u, v) representing an edge from u to v,
#                 and values are the edge weights.
# Returns:
#     list: A list of strings representing the shortest path from source 
#           to destination. Returns an empty list if no path is found.
#############################################################################
def HPV_GetShortestPath(source, destination, map):
    # Build adjacency list, considering bidirectional edges
    graph = {}
    nodes = set()
    for (u, v), w in map.items():
        if u not in graph:
            graph[u] = []
        if v not in graph:
            graph[v] = []
        graph[u].append((v, w))  # Original edge
        graph[v].append((u, w))  # Reverse edge (bidirectional)
        nodes.add(u)
        nodes.add(v)

    # Priority queue for Dijkstra's algorithm
    pq = []
    heapq.heappush(pq, (0, source, [source]))  # (distance, current_node, path)

    # Distance dictionary to track minimum distances
    distances = {node: float('inf') for node in nodes}
    distances[source] = 0

    while pq:
        current_distance, current_node, path = heapq.heappop(pq)

        if current_node == destination:
            print("The Calculated shortest path from ", source, " to ", destination, " is: ", path)
            return path

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor, path + [neighbor]))

    return []  # No path found

#############################################################################
#                                  M A I N                                  #
#############################################################################
#############################################################################
# Function: main
# Description: Initializes the High-Power Vehicle (HPV) server, listens for 
#              incoming requests from Low-Power Vehicles (LPVs), retrieves 
#              graph weights from the Cloud Server, calculates the shortest 
#              path, and sends the result back to the LPV. Runs continuously.
# Args: None
# Returns: None
#############################################################################
def main():
    # Initialize the HPV Server socket 
    HpvServerSocket = HPV_InitServer()

    # Run the HPV continously
    while True:
        # Wait for a request from an LPV
        LpvSocket = HPV_WaitForLpvSession(HpvServerSocket)

        # Check that an LPV socket is initiated correctly
        if LpvSocket is not None:
            # Receive Source and Destination from the LPV
            source, destination = HPV_ReceiveLpvRequest(LpvSocket)

        # Connect to the Cloud Server to receive the weights
        CloudServerSocket = HPV_ConnectToCloudServer()

        # Check that the Cloud Server socket is initiated correctly
        if CloudServerSocket is not None:
            # Receive the Weights from the Cloud Server
            receivedWeights = HPV_ReceiveWeights(CloudServerSocket)

            # Perform Dijksta's Algorithm to find the shortest path between the source and the destination
            shortestPath = HPV_GetShortestPath(source, destination, receivedWeights)

            # Send the shortest path to the LPV
            HPV_SendShortestPath(LpvSocket, shortestPath)

        # Close Sokets with the Cloud Server and the LPV
        CloudServerSocket.close()
        LpvSocket.close()

if __name__ == "__main__":
    main()