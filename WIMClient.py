import json
import socket
import subprocess
from multiprocessing import Process

global MYPORT
users = []
java_sender_port = 0

proxy_IP = '10.220.89.187'
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


def request_users():
    # Connect to the proxy server
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect((proxy_IP, 12342))

    # Send request message
    s1.sendall("REQUEST".encode(ENCODE))
    ret = json.loads(s1.recv(4096).decode(ENCODE))
    s1.close()
    return ret


def get_name() -> str:
    # Connect to the Java GUI

    name_socket.listen(1)

    name_sender_socket = name_socket.accept()

    # Accept the name from the Java GUI
    found_name = name_sender_socket[0].recv(1024).decode(ENCODE).strip()

    name_socket.close()

    return found_name


# Currently hard-coded to Quentyn's IP address, proxy server will run on his on the local Eduroam network
def find_addresses(name, my_port) -> list:
    # Connect to the proxy server
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2.connect((proxy_IP, 12342))

    # Send port number and name to proxy server for storage
    s2.sendall(str(my_port).encode(ENCODE))
    s2.recv(1024)
    s2.sendall(name.encode(ENCODE))

    # Collect all current users in server, including self
    user_data = s2.recv(4096).decode(ENCODE).strip()

    s2.close()
    return json.loads(user_data)


def send_message(message):
    # Iterate through the list of current users
    for user in users:
        print("sending")
        # Send to the java sender socket if sending a message to yourself
        if user[0] == screen_name:
            # Connect to the java socket listening for messages to be displayed
            java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            java_sender_socket.connect(('localhost', java_sender_port))

            # Send message and name for the Java GUI to display
            java_sender_socket.sendall((screen_name + ": " + message).encode())
            java_sender_socket.close()
            print("Message sent to Java GUI\n")
        else:
            # Connect to user socket
            send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(user[2], user[1])
            send.connect((user[2], user[1]))
            send.sendall(message.encode())
            print("Message sent to user")
            send.close()  # Close the socket after sending the message


def handle_client(client, addr, java_sender_port, screen_name):
    users = request_users()
    print("Handling")
    other_name = ''
    for user in users:
        if user[2] == addr[0] and user[0] != screen_name:
            other_name = user[0]
            continue

    # Accept the message being sent
    incoming_message = client.recv(2048).decode(ENCODE).strip()
    if incoming_message != exit_message:

        print(other_name, ":", incoming_message)

        # Connect to the java socket listening for messages to be displayed
        java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("java port: ", java_sender_port)
        java_sender_socket.connect(('127.0.0.1', java_sender_port))

        # Send message and name for the Java GUI to display
        java_sender_socket.sendall((other_name + ": " + incoming_message).encode())
        java_sender_socket.close()
        print("Message sent to Java GUI\n")

    else:
        # Remove user that has requested to leave
        for user in users:
            if user[2] == addr[0]:
                other_name = user[0]
                java_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                java_sender_socket.connect(('127.0.0.1', java_sender_port))
                java_sender_socket.sendall((other_name + " has disconnected").encode())
                java_sender_socket.close()
                users.remove(user)
    print("Not handling client anymore")


def listen_for_users(MYPORT, java_sender_port, screen_name):
    # Wait for new user to send a message
    host = ''
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind((host, MYPORT))
    listener.listen()

    while True:
        # Accept new user
        print(f"Listening on {(host, MYPORT)}")
        new_client, addr = listener.accept()
        print("found user who wants to say something")

        # Create a new process to handle this new client
        handle_client(new_client, addr, java_sender_port, screen_name)
        new_client.close()


def remove_from_proxy():
    # Connect to the proxy server
    s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s3.connect((proxy_IP, 12342))

    # Send remove message
    s3.sendall("REMOVE".encode(ENCODE))
    # Wait for a response
    s3.recv(1024)
    # Send screen name to the server
    s3.sendall(screen_name.encode(ENCODE))


if __name__ == '__main__':
    # Create a socket to listen for connections from the Java GUI
    java_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    java_receiver_socket.bind(('localhost', 0))
    java_receiver_socket.listen(1)

    name_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name_socket.bind(('localhost', 0))

    java_args.append(str(java_receiver_socket.getsockname()[1]))
    java_args.append(str(name_socket.getsockname()[1]))

    # Run the Java GUI using subprocess
    subprocess.Popen(java_args)

    js, address = java_receiver_socket.accept()
    java_sender_port = int(js.recv(2048).decode(ENCODE))
    js.close()
    print(java_sender_port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))

    MYPORT = s.getsockname()[1]
    s.close()
    print("port:", MYPORT)

    try:
        screen_name = get_name()

        while MYPORT == 0:
            continue

        users = find_addresses(screen_name, MYPORT)
        print(users)
    except:
        print("Couldn't connect to server")
        exit(0)

    listener_process = Process(target=listen_for_users, args=(MYPORT, java_sender_port, screen_name))
    listener_process.start()

    connected = True
    send_message("has connected")
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

        users = request_users()
        print(users)
        # Send the message out to users
        send_message(user_input)

        # Close the sender socket
        js.close()

    # Close the receiver socket and listener process
    remove_from_proxy()
    java_receiver_socket.close()
    listener_process.join(0.1)

    listener_process.terminate()

    exit(2)
