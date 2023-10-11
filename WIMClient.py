import socket
import subprocess

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
