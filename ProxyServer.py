import json
import socket

PORT = 12342
ENCODE = 'utf-8'

users = []  # name, port, IP


def remove_client(name, address):
    for user in users:
        if user[2] == address[0] and user[0] == name:
            print("removing")
            users.remove(user)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))

s.listen(30)

while True:
    cs, addr = s.accept()

    # Collect the name and the port number of the new user
    port = cs.recv(2048).decode(ENCODE).strip()

    if port == "REMOVE":  # Removing a client from the list of currently online users
        cs.sendall("a".encode(ENCODE))
        name = cs.recv(2048).decode(ENCODE).strip()
        remove_client(name, addr)
    else:  # Receive information from user and add it to the list and give them the list of users
        cs.sendall(port.encode(ENCODE))
        name = cs.recv(2048).decode(ENCODE).strip()

        # Add the new user's information to the collection of current users
        users.append([name, int(port), addr[0]])  # [Name, port #, IP#]

        # Serialize the user data and send it to the new user
        user_data = json.dumps(users)
        cs.sendall(user_data.encode(ENCODE))

    cs.close()

s.close()
