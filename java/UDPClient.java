import java.net.*;

public class UDPClient {
    public static void main(String[] args) {
        DatagramSocket socket = null;

        try {
            // Create a UDP socket
            socket = new DatagramSocket();

            // Specify the IP address and port number of the server
            InetAddress serverAddress = InetAddress.getByName("localhost");
            int serverPort = 8080;

            // Create a message to send
            String message = "Hello, server!";
            byte[] messageBytes = message.getBytes();

            // Create a datagram packet containing the message
            DatagramPacket packet = new DatagramPacket(messageBytes, messageBytes.length, serverAddress, serverPort);

            // Send the packet to the server
            socket.send(packet);

            // Receive a response from the server
            byte[] responseBytes = new byte[1024];
            DatagramPacket responsePacket = new DatagramPacket(responseBytes, responseBytes.length);
            socket.receive(responsePacket);

            // Convert the response to a string and print it
            String response = new String(responsePacket.getData(), 0, responsePacket.getLength());
            System.out.println("Received response from server: " + response);
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}