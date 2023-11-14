import json
import socket
import subprocess
import random
from multiprocessing import Process

MYPORT = random.randint(20000, 60000)

exit_message = "☻♥♦♣♠•◘○◙"
java_gui_jar_path = "WIM.jar"
ENCODE = 'utf-8'
java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    # Connect to the Java GUI
    name_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name_socket.bind(('localhost', 22222))
    name_socket.listen(1)

    name_sender_socket = name_socket.accept()

    # Accept the name from the Java GUI
    found_name = name_sender_socket[0].recv(1024).decode(ENCODE).strip()

    name_socket.close()

    return found_name


def find_addresses(name, my_port) -> list:
    # Connect to the proxy server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.220.90.135', 12342))

    # Send port number and name to proxy server for storage
    s.sendall(str(my_port).encode(ENCODE))
    s.recv(1024)
    s.sendall(name.encode(ENCODE))

    # Collect all current users in server, including self
    user_data = s.recv(4096).decode(ENCODE).strip()

    s.close()
    return json.loads(user_data)


def send_message(message):
    # Iterate through the list of current users
    for user in users:
        print("sending")
        # Send to the java sender socket if sending a message to yourself
        if user[2] == socket.gethostbyname(socket.gethostname()):
            # Connect to the java socket listening for messages to be displayed
            java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            java_sender_socket.connect(('localhost', 65535))

            # Send message and name for the Java GUI to display
            java_sender_socket.sendall(message.encode())
            java_sender_socket.sendall(screen_name.encode())
            java_sender_socket.close()
            print("Message sent to Java GUI\n")
        else:
            # Connect to user socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((user[2], user[1]))
            s.sendall(message.encode())
            s.sendall(user[0].encode())
            print("Message sent to user")
            s.close()  # Close the socket after sending the message


def handle_client(client, addr):
    # name = "notfound"
    # while name == "notfound":
    for user in users:
        if user[2] == addr[0]:
            name = user[0]
    #     remove_from_proxy()
    #     users = find_addresses(screen_name, MYPORT)

    while True:
        print("Handling")
        # Accept the message being sent
        incoming_message = client.accept(2048).decode(ENCODE)
        if incoming_message != exit_message:
            # Give the message to the Java GUI
            java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            java_sender_socket.connect(('localhost', 65535))
            java_sender_socket.send(incoming_message.encode())
            java_sender_socket.send(name.encode())

        else:
            # Remove user that has requested to leave
            for user in users:
                if user[2] == addr[0]:
                    users.remove(user)
            break
    print("Not handling client anymore")


def listen_for_users():
    # Wait for new user to send a message
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('localhost', MYPORT))
    listener.listen(30)

    while True:
        # Accept new user
        print("listening")
        new_client, addr = listener.accept()

        # Create a new process to handle this new client
        client_process = Process(target=handle_client, args=(new_client, addr))
        client_process.start()


def remove_from_proxy():
    # Connect to the proxy server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('10.220.90.135', 12342))

    # Send remove message
    s.sendall("REMOVE".encode(ENCODE))
    # Wait for a response
    s.recv(1024)
    # Send screen name to the server
    s.sendall(screen_name.encode(ENCODE))


if __name__ == '__main__':
    # Run the Java GUI using subprocess
    subprocess.Popen(java_args)

    # Create a socket to listen for connections from the Java GUI
    java_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    java_receiver_socket.bind(('localhost', 12345))
    java_receiver_socket.listen(1)

    screen_name = get_name()
    users = find_addresses(screen_name, MYPORT)
    print(users)

    listener_process = Process(target=listen_for_users)
    listener_process.start()

    connected = True
    while connected:

        print("Waiting for Java GUI to send a message...")

        # Accept a connection from the Java GUI
        js, address = java_receiver_socket.accept()
        print(f"Connected to {address}")

        # Receive user input from the Java GUI
        user_input = js.recv(2048).decode(ENCODE)
        print("Message received from Java GUI")

        if user_input.strip() == exit_message:
            connected = False
            remove_from_proxy()

        remove_from_proxy()
        users = find_addresses(screen_name, MYPORT)
        print(users)

        # Send the message out to users
        send_message(user_input)

        # Close the sender socket
        js.close()

    # Close the receiver socket and listener process
    java_receiver_socket.close()
    listener_process.join(0.1)

    listener_process.terminate()

    exit(2)
