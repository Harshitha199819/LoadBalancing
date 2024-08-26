import socket

def send_request(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('172.31.8.174', 8080))  # Replace with your Load Balancer's private IP
    client_socket.send(message.encode('utf-8'))

    # Receive the response from the load balancer
    response = client_socket.recv(1024).decode('utf-8')
    print(f"Client received response: {response}")
    client_socket.close()

if __name__ == "__main__":
    for i in range(5):  # Sending multiple requests to demonstrate load balancing
        send_request(f"Request {i+1}")
