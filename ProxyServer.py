import json
import socket

PORT = 12342
ENCODE = 'utf-8'

users = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', PORT))

s.listen(30)

while True:
    cs, addr = s.accept()

    # Collect the name and the port number of the new user
    port = cs.recv(2048).decode(ENCODE).strip()
    cs.sendall(port.encode(ENCODE))
    name = cs.recv(2048).decode(ENCODE).strip()

    # Add the new user's information to the collection of current users
    users.append([name, int(port), addr[0]])

    # Serialize the user data and send it to the new user
    user_data = json.dumps(users)
    cs.sendall(user_data.encode(ENCODE))

    cs.close()


s.close()