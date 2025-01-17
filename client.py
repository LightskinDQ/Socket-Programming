import socket

SERVER_HOST = '127.0.0.1'  # Localhost
SERVER_PORT = 65432        # Port used by the server

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to the server
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"Connected to the server at {SERVER_HOST}:{SERVER_PORT}")

            # Client Server interaction
            while True:
                # Read user input
                user_input = input("Enter command (message, status, list, get <filename>, exit): ").strip()

                # Send the user input to the server
                client_socket.sendall(user_input.encode('utf-8'))

                if user_input.lower() == 'exit':
                    # Disconnect from the server
                    print("Disconnecting from the server...")
                    break

                # Receive the response from the server
                response = client_socket.recv(1024).decode('utf-8')
                print("Server response:", response)

        except ConnectionRefusedError:
            print("Could not connect to the server. Please ensure the server is running.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    start_client()
