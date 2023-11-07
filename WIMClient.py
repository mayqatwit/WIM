import json
import socket
import subprocess
import random

MYPORT = random.randint(20000,60000)


def find_addresses(name, my_port):
    # Connect to the proxy server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 12342))

    # Send port number and name to proxy server for storage
    s.send(str(my_port).encode('utf-8'))
    s.recv(1024)
    s.send(name.encode('utf-8'))

    # Collect all current users in server, including self
    user_data = s.recv(4096).decode('utf-8').strip()

    s.close()
    return json.loads(user_data)


def get_name() -> str:
    name_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name_socket.bind(('localhost', 22222))
    name_socket.listen(1)

    name_sender_socket, address = name_socket.accept()

    name = name_sender_socket.recv(1024).decode('utf-8').strip()

    name_socket.close()

    return name


def send_message():
    pass


def receive_message():
    pass


exit_message = "EXIT"

java_gui_jar_path = "WIM.jar"

# Specify the Java module path and modules as separate arguments
java_args = [
    "java",
    "--module-path",
    "javafx-sdk-19.0.2.1/lib",
    "--add-modules",
    "javafx.controls,javafx.fxml",
    "-jar",
    java_gui_jar_path,
]

# Run the Java GUI using subprocess
subprocess.Popen(java_args)

users = find_addresses(get_name(), MYPORT)

print(users)

# Create a socket to listen for connections from the Java GUI
java_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
java_receiver_socket.bind(('localhost', 12345))
java_receiver_socket.listen(1)

connected = True
while connected:

    print("Waiting for Java GUI to send a message...")

    # Accept a connection from the Java GUI
    java_sender_socket, address = java_receiver_socket.accept()
    print(f"Connected to {address}")

    # Receive user input from the Java GUI
    user_input = java_sender_socket.recv(2048).decode('utf-8')
    print("Message received from Java GUI")

    if user_input.strip() == exit_message:
        connected = False
        break

    # Stores result
    result = f"{user_input}"

    # Send the result back to the Java GUI
    java_sender_socket.send(result.encode())
    print("Message sent to Java GUI\n")

    # Close the sender socket
    java_sender_socket.close()

# Close the receiver socket
java_receiver_socket.close()
