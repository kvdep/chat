import socket
import threading

HOST = 'localhost'   # Listen on all available interfaces
PORT = 12345

clients = []

def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    clients.append(client_socket)
    broadcast(f"[SERVER] {client_address} joined the chat.", client_socket)
    
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{client_address}] {message}")
            broadcast(f"[{client_address}] {message}", client_socket)
    except ConnectionResetError:
        print(f"[DISCONNECT] {client_address} disconnected.")
    finally:
        clients.remove(client_socket)
        broadcast(f"[SERVER] {client_address} left the chat.", client_socket)
        client_socket.close()

def broadcast(message, sender_socket=None):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            clients.remove(client)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    
    while True:
        client_socket, client_address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()