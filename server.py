import socket
import threading
import os
from datetime import datetime

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Arbitrary port for the server
MAX_CLIENTS = 3     # Maximum number of simultaneous clients
FILE_REPOSITORY = './files/'  # Directory where files are stored

# Cache to keep track of connected clients
client_cache = {}

# Function to handle individual client connection
def handle_client(conn, addr, client_name):
    print(f"[{client_name}] connected from {addr}.")
    connection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_cache[client_name] = {
        "address": addr,
        "connected_at": connection_time,
        "disconnected_at": None
    }

    try:
        while True:
            # Receive message from the client
            message = conn.recv(1024).decode('utf-8').strip()
            if not message:
                continue

            print(f"[{client_name}] action: {message}")

            if message.lower() == 'exit':
                # Disconnect the client
                print(f"[{client_name}] has disconnected.")
                disconnection_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                client_cache[client_name]["disconnected_at"] = disconnection_time
                break

            elif message.lower() == 'status':
                # Send the current status of client cache
                status_message = "\n".join([f"{name}: {details}" for name, details in client_cache.items()])
                conn.sendall(status_message.encode('utf-8'))
                print(f"[{client_name}] requested status: {status_message}")

            elif message.lower() == 'list':
                # List files in the repository as a comma-separated string
                try:
                    files = os.listdir(FILE_REPOSITORY)
                    files_list = ", ".join(files) if files else "No files available."
                    conn.sendall(files_list.encode('utf-8'))
                    print(f"[{client_name}] requested file list: {files_list}")
                except FileNotFoundError:
                    error_message = "File repository not found."
                    conn.sendall(error_message.encode('utf-8'))
                    print(f"[{client_name}] error: {error_message}")

            elif message.startswith('get '):
                # Handle file request
                filename = message[4:].strip()
                file_path = os.path.join(FILE_REPOSITORY, filename)
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        file_data = file.read()
                        conn.sendall(file_data)
                    print(f"[{client_name}] requested file '{filename}' - File sent")
                else:
                    error_message = f"File '{filename}' not found."
                    conn.sendall(error_message.encode('utf-8'))
                    print(f"[{client_name}] error: {error_message}")

            else:
                # Echo message back to the client with "ACK" appended
                ack_message = f"{message} ACK"
                conn.sendall(ack_message.encode('utf-8'))
                print(f"[{client_name}] message echoed: {ack_message}")

    except Exception as e:
        print(f"An error occurred with [{client_name}]: {str(e)}")
    
    finally:
        # Clean up the connection
        conn.close()
        del client_cache[client_name]
        print(f"[{client_name}] connection closed.")

# Main server function to accept new client connections
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server started on {HOST}:{PORT}")

        while True:
            # Accept new connections
            conn, addr = server_socket.accept()

            # Limit number of clients
            if len(client_cache) >= MAX_CLIENTS:
                print(f"[{addr}] connection attempt rejected: Server is at full capacity.")
                conn.sendall("Server is at full capacity. Try again later.".encode('utf-8'))
                conn.close()
                continue

            # Assign client name
            client_name = f"Client{len(client_cache) + 1:02d}"
            # Start a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, client_name))
            client_thread.start()

if __name__ == "__main__":
    start_server()

