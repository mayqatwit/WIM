import json
import socket
import subprocess
import random
import threading
import multiprocessing
from multiprocessing import Process

MYPORT = random.randint(20000, 60000)

exit_message = "EXIT"
java_gui_jar_path = "WIM.jar"
ENCODE = 'utf-8'
terminate_process = False

# The Java module path and modules for the .jar file
java_args = [
    "java",
    "--module-path",
    "javafx-sdk-19.0.2.1/lib",
    "--add-modules",
    "javafx.controls,javafx.fxml",
    "-jar",
    java_gui_jar_path,
]


def get_name() -> str:
    name_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name_socket.bind(('localhost', 22222))
    name_socket.listen(1)

    name_sender_socket = name_socket.accept()

    found_name = name_sender_socket[0].recv(1024).decode(ENCODE).strip()

    name_socket.close()

    return found_name


def find_addresses(name, my_port) -> list:
    # Connect to the proxy server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 12342))

    # Send port number and name to proxy server for storage
    s.sendall(str(my_port).encode(ENCODE))
    s.recv(1024)
    s.sendall(name.encode(ENCODE))

    # Collect all current users in server, including self
    user_data = s.recv(4096).decode(ENCODE).strip()

    s.close()
    return json.loads(user_data)


def send_message(message):
    for user in users:
        print("sending")
        if user[2] == '10.220.90.135':
            java_sender_socket.send(message.encode())
            print("Message sent to Java GUI\n")

        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((user[2], user[1]))

            s.sendall(message.encode(ENCODE))
            print("Message sent to user")


def handle_client(client, address):
    while not terminate_process:
        print("Handling")
        incoming_message = client.accept(2048).decode(ENCODE)
        java_sender_socket.send(incoming_message.encode())


def listen_for_users():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', MYPORT))
    listener.listen(30)

    while not terminate_process:
        print("listening")
        new_client, addr = listener.accept()

        client_process = Process(target=handle_client, args=(new_client, addr))
        client_process.start()
        client_process.join()


if __name__ == '__main__':
    # Run the Java GUI using subprocess
    subprocess.Popen(java_args)

    screen_name = get_name()
    users = find_addresses(screen_name, MYPORT)
    print(users)

    # Create a socket to listen for connections from the Java GUI
    java_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    java_receiver_socket.bind(('localhost', 12345))
    java_receiver_socket.listen(1)

    # Start a thread to listen for new clients sending messages
    #listener_thread = threading.Thread(target=listen_for_users)
    #listener_thread.start()

    listener_process = Process(target=listen_for_users)
    listener_process.start()
    #listener_process.join()

    connected = True
    while connected:

        print("Waiting for Java GUI to send a message...")

        # Accept a connection from the Java GUI
        java_sender_socket, address = java_receiver_socket.accept()
        print(f"Connected to {address}")

        # Receive user input from the Java GUI
        user_input = java_sender_socket.recv(2048).decode(ENCODE)
        print("Message received from Java GUI")

        if user_input.strip() == exit_message:
            connected = False

        # Stores result
        result = f"{user_input}"

        send_message(result)

        # Close the sender socket
        java_sender_socket.close()

    # Close the receiver socket
    java_receiver_socket.close()
    listener_process.join()

    listener_process.terminate()
    exit(2)
