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
    port = cs.recv(1024).decode('utf-8').strip()
    cs.send(port.encode('utf-8'))
    name = cs.recv(1024).decode('utf-8').strip()

    # Add the new users information to the collection of current users
    users.append((name, port, addr))

    # Send all the current user data to the new user, so they can communicate with everyone
    for user in users:
        cs.send(user[0].encode('utf-8'))
        cs.send(user[1].encode('utf-8'))
        cs.send(user[2][0].encode('utf-8'))

    cs.send("EXIT".encode('utf-8'))

    cs.close()


s.close()