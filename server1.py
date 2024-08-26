import socket
import threading
import time
import sys

def send_health_status(server_id, lb_host, lb_port):
    while True:
        try:
            health_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            health_socket.connect((lb_host, lb_port))
            health_message = f"Server-{server_id}: healthy"
            health_socket.send(health_message.encode('utf-8'))
            health_socket.close()
        except Exception as e:
            print(f"Error sending health status: {e}")
        time.sleep(3)  # Send health status every 3 seconds

def send_kill_signal(server_id, lb_host, lb_port):
    try:
        kill_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        kill_socket.connect((lb_host, lb_port))
        kill_message = f"Server-{server_id}: kill"
        kill_socket.send(kill_message.encode('utf-8'))
        kill_socket.close()
    except Exception as e:
        print(f"Error sending kill signal: {e}")

def start_server(server_id, port, lb_host, lb_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))  # Bind to all network interfaces
    server_socket.listen(5)
    print(f"Backend Server {server_id} listening on port {port}...")

    # Start a thread to send health status to the load balancer
    health_thread = threading.Thread(target=send_health_status, args=(server_id, lb_host, lb_port))
    health_thread.daemon = True
    health_thread.start()

    try:
        while True:
            client_socket = None
            try:
                client_socket, addr = server_socket.accept()
                print(f"Server {server_id} received connection from {addr}")

                request = client_socket.recv(1024).decode('utf-8')
                print(f"Server {server_id} received request: {request}")

                # Respond to the load balancer
                response = f"Response from Server {server_id}"
                client_socket.send(response.encode('utf-8'))
            except Exception as e:
                print(f"Error handling request: {e}")
            finally:
                if client_socket:
                    client_socket.close()
    except KeyboardInterrupt:
        print(f"Server {server_id} shutting down...")
        send_kill_signal(server_id, lb_host, lb_port)

if __name__ == "__main__":
    server_id = 1  # Update this ID for each server instance
    port = 9008  # Update this port for each server instance
    lb_host = '172.31.8.174'  # Load balancer IP address
    lb_port = 9090  # Health check port on the load balancer
    start_server(server_id, port, lb_host, lb_port)
