import socket
import threading
import time

def send_health_status(server_id, lb_host, lb_port):
    while True:
        health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        health_socket.connect((lb_host, lb_port))
        health_message = f"Server-{server_id}: healthy"
        health_socket.send(health_message.encode('utf-8'))
        health_socket.close()
        time.sleep(3)  # Send health status every 3 seconds

def start_server(server_id, port, lb_host, lb_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Backend Server {server_id} listening on port {port}...")

    # Start a thread to send health status to the load balancer
    health_thread = threading.Thread(target=send_health_status, args=(server_id, lb_host, lb_port))
    health_thread.daemon = True
    health_thread.start()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Server {server_id} received connection from {addr}")
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Server {server_id} received request: {request}")

        # Respond to the load balancer
        response = f"Response from Server {server_id}"
        client_socket.send(response.encode('utf-8'))
        client_socket.close()

if __name__ == "__main__":
    start_server(server_id=1, port=9009, lb_host='172.31.8.174', lb_port=9090)  # Update lb_host with Load Balancer's private IP
    # Run a second instance with:
    # start_server(server_id=2, port=9009, lb_host='10.0.1.12', lb_port=9090)
