package runable;

import java.util.Date;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.ResourceBundle;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.ScrollPane;
import javafx.scene.control.TextField;
import javafx.scene.image.Image;
import javafx.scene.input.KeyCode;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.stage.Stage;

public class Main extends Application implements Initializable {

	@FXML
	TextField enterName;
	@FXML
	TextField enterText;
	@FXML
	TextFlow displayText;
	@FXML
	ScrollPane scrollPane;
	@FXML
	Button exitButton;
	String name;

	class MultithreadingDemo extends Thread {
	    public void run()
	    {
	        try {
	           receiveMessages();
	        }
	        catch (Exception e) {
	            // Throwing an exception
	            System.out.println(e);
	            System.out.println("Error in thread");
	        }
	    }
	}

	public static void main(String[] args) {

		launch(args);

	}

	@Override
	public void start(Stage primaryStage) throws Exception {
		Parent p = FXMLLoader.load(getClass().getResource("WIM.v.2.fxml"));

		Scene root = new Scene(p);
		primaryStage.setScene(root);
		primaryStage.setTitle("WIM: Wentworth Instant Messaging");
		primaryStage.getIcons().add(new Image("images/e35495597930766.png"));
		primaryStage.setResizable(false);
		primaryStage.show();

	}

	@Override
	public void initialize(URL location, ResourceBundle resources) {
		MultithreadingDemo object
        = new MultithreadingDemo();
    object.start();

		enterName.setOnKeyPressed((e) -> {

			if (e.getCode().equals(KeyCode.ENTER)) {
				name = enterName.getText();
				if (name != null) { // Make sure they entered a name
					if (name.length() < 16) { // Name is <= 15 characters
						enterName.setDisable(true);
						try {
							Socket socket = new Socket("localhost", 22222);
							PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
							out.println(name);
							socket.close();
						} catch (IOException e1) {
						}

					} else { // Error message for name being too long
						Text t = new Text(String.format("Please make your screen name less than 15 characters%n"));
						t.setFill(Color.RED);
						displayText.getChildren().add(t);
						name = null;
					}
				}
			}

		});

		enterText.setOnKeyPressed((e) -> {

			if (e.getCode().equals(KeyCode.ENTER)) {
				String message = enterText.getText();
				if (message != "") {
					if (name != null) { // Must have a screen name set before sending a message
						enterText.clear();
						// Create a socket to connect to the Python script
						Socket socket;

						try {
							// Create a socket to connect to the Python script
							socket = new Socket("localhost", 12345);

							// Send the user input to the Python script
							PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
							out.println(message);
//
//							// Receive the result from the Python script
//							BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
//							String result = in.readLine();
//
//							// Display the message from the Python script
//							displayText.getChildren()
//									.add(new Text(String.format("[%s] %s: %s%n", getTime(), name, result)));

							// Close the socket
							socket.close();

						} catch (IOException e1) {
							e1.printStackTrace();
						}

					} else { // Error message for not having a screen name
						Text t = new Text(String.format("Please enter a screen name before messaging%n"));
						t.setFill(Color.RED);
						displayText.getChildren().add(t);
					}
				}
			}
		});

		exitButton.setOnAction((e) -> {
			try {
				Socket socket = new Socket("localhost", 12345);
				PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
				out.println("☻♥♦♣♠•◘○◙");
				socket.close();
				System.exit(0);
			} catch (IOException e1) {
			}
		});

	}

	/**
	 * Method to return the current time in HH:MM:SS format
	 *
	 * @return string time in HH:MM:SS format
	 */
	public static String getTime() {
		String date = new Date().toString();
		String[] s = date.split(" ");

		return s[3];

	}

	public void receiveMessages() throws UnknownHostException, IOException {
		ServerSocket serverSocket = new ServerSocket( 65535 );

		while (true) {
			System.out.println("Wating for new message");

			// Receive the result from the Python script
			Socket listen = serverSocket.accept();
			BufferedReader in = new BufferedReader(new InputStreamReader(listen.getInputStream()));
			String message = in.readLine();
			String name = in.readLine();

			// Display the message from the Python script
	        Platform.runLater(() -> {
	            displayText.getChildren().add(new Text(String.format("[%s] %s: %s%n", getTime(), name, message)));
	        });
			// Close the socket
			listen.close();
		}
	}
}
