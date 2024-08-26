import socket
import threading

# Use the private IP addresses of your backend servers
backend_servers = [("172.31.7.238", 9008), ("172.31.8.222", 9009)]  # Replace with your private IPs
current_server = 0
health_status = {9008: False, 9009: False}  # Tracks the health of each server

def round_robin():
    global current_server
    available_servers = [server for server in backend_servers if health_status[server[1]]]
    if not available_servers:
        return None  # No healthy servers available
    server = available_servers[current_server % len(available_servers)]
    current_server = (current_server + 1) % len(available_servers)
    return server

def listen_for_health_updates(lb_port):
    health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    health_socket.bind(('0.0.0.0', lb_port))
    health_socket.listen(5)
    print(f"Load Balancer health listener running on port {lb_port}...")

    while True:
        conn, addr = health_socket.accept()
        health_message = conn.recv(1024).decode('utf-8')
        print(f"Received health update: {health_message}")

        # Parse the health message and update the status map
        if "healthy" in health_message:
            server_id = int(health_message.split('-')[1].split(':')[0])
            port = 9007 + server_id  # Adjusting the port based on server_id
            health_status[port] = True
        conn.close()

def start_load_balancer():
    lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lb_socket.bind(('0.0.0.0', 8080))
    lb_socket.listen(5)
    print("Load Balancer listening on port 8080...")

    # Start a thread to listen for health updates from backend servers
    health_thread = threading.Thread(target=listen_for_health_updates, args=(9090,))
    health_thread.daemon = True
    health_thread.start()

    while True:
        client_socket, addr = lb_socket.accept()
        print(f"Load Balancer received connection from {addr}")

        request = client_socket.recv(1024).decode('utf-8')
        print(f"Load Balancer received request: {request}")

        # Determine which backend server to forward the request to
        backend_server = round_robin()

        if backend_server is None:
            print("No healthy servers available. Responding with 503.")
            client_socket.send(b"HTTP/1.1 503 Service Unavailable\r\n\r\n")
            client_socket.close()
            continue

        # Forward the request to the selected backend server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(backend_server)
        server_socket.send(request.encode('utf-8'))

        # Receive the response from the backend server
        response = server_socket.recv(1024)
        try:
            response = response.decode('utf-8')
        except UnicodeDecodeError:
            print("Received non-text data, handling it as raw bytes.")

        server_socket.close()

        # Send the response back to the client
        client_socket.send(response.encode('utf-8') if isinstance(response, str) else response)
        client_socket.close()

if __name__ == "__main__":
    start_load_balancer()
