package functions

import (
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// getClientIP Get the public IP of the client
func getClientIP() (string, error) {
	// Get HTTP response from https://api.ipify.org
	resp, err := http.Get("https://api.ipify.org")
	if err != nil {
		log.Print("Error getting IP address:", err)
		log.Print("Trying another way")
		return getClientIP2()
	}
	defer resp.Body.Close()

	// Get the public IP address from the response body
	ip, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Print("Error reading IP address:", err)
		return "", err
	}

	return string(ip), nil
}

// getClientIP2 Get the private IP of the client if getClientIP() fails
func getClientIP2() (string, error) {
	// Start a UDP connection to 8:8:8:8:80
	conn, err := net.Dial("udp", "8.8.8.8:80")
	if err != nil {
		log.Print("Error getting IP address:", err)
		return "", err
	}
	defer conn.Close()

	// Get the private IP address from LocalAddr()
	localAddr := conn.LocalAddr().(*net.UDPAddr)

	return localAddr.IP.String(), nil
}

// connect Start a UDP connection to the server
func connect() (*net.UDPConn, string, error) {
	// Convert the server IP address and port into *UDPAddr type
	udpServer, err := net.ResolveUDPAddr(Type, fmt.Sprintf("%s:%s", Host, Port))
	if err != nil {
		log.Print("ResolveUDPAddr failed:", err.Error())
		return nil, "", err
	}

	// Start a connection to the UDP server
	conn, err := net.DialUDP(Type, nil, udpServer)
	if err != nil {
		log.Print("Listen failed:", err.Error())
		return nil, "", err
	}

	// Get the IP of the client
	ip, err := getClientIP()
	if err != nil {
		log.Print("Error getting IP:", err)
		return nil, "", err
	}

	return conn, ip, nil
}

// listener Start a UDP listener connection for monitoring flight
func listener() (*net.UDPConn, string, error) {
	// Convert the Client local IP into a *UDPAddr type
	addr := &net.UDPAddr{IP: net.ParseIP(ClientHost)}

	// Start a UDP listener
	conn, err := net.ListenUDP(Type, addr)
	if err != nil {
		log.Print("Error opening UDP connection:", err)
		return nil, "", err
	}

	// Get the IP of the client
	ip, err := getClientIP()
	if err != nil {
		log.Print("Error getting IP:", err)
		return nil, "", err
	}

	return conn, ip, nil
}

// sendToServer Send message to the server
func sendToServer(conn *net.UDPConn, bytes_ []byte, packetLoss int32) ([]byte, error) {
	var received []byte
	for i := 0; i < MaxRetries; i++ {
		// Turn off the simulated packet loss byte when we retry the 4th time
		if i == 3 {
			bytes_ = utlis.TurnPacketLossOff(bytes_)
		}

		// Send the message to the server
		_, err := conn.Write(bytes_)
		if err != nil {
			log.Print("Write data failed:", err.Error())
			return nil, err
		}

		// Set the response timeout
		conn.SetReadDeadline(time.Now().Add(Deadline))
		received = make([]byte, 4096)
		// Read the response from the server
		_, err = conn.Read(received)
		if err == nil {
			break
		}

		// Check if the error is a timeout error or other errors
		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			msg := fmt.Sprintf("Retrying. No.%d", i+1)
			fmt.Printf("%s\n", text.FgRed.Sprintf("%s", msg))
			if i == MaxRetries-1 {
				return nil, errors.New("Max retries reached!")
			}
		} else {
			log.Print("Read data failed:", err.Error())
			return nil, err
		}
	}

	return received, nil
}

// sendToServerAsListener Send message to the server as a listener
func sendToServerAsListener(conn *net.UDPConn, bytes_ []byte, packetLoss int32) ([]byte, []byte, error) {
	var received []byte

	udpServer, err := net.ResolveUDPAddr(Type, fmt.Sprintf("%s:%s", Host, Port))
	if err != nil {
		log.Print("ResolveUDPAddr failed:", err.Error())
		return nil, nil, err
	}

	for i := 0; i < MaxRetries; i++ {
		// Turn off the simulated packet loss byte when we retry the 4th time
		if i == 3 {
			bytes_ = utlis.TurnPacketLossOff(bytes_)
		}

		// Send the message to the server
		_, err = conn.WriteToUDP(bytes_, udpServer)
		if err != nil {
			log.Print("Write data failed:", err.Error())
			return nil, nil, err
		}

		// Set the response timeout
		conn.SetReadDeadline(time.Now().Add(Deadline))
		received = make([]byte, 4096)
		// Read the response from the server
		_, _, err = conn.ReadFrom(received)
		if err == nil {
			break
		}

		// Check if the error is a timeout error or other errors
		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			fmt.Printf("Retrying. No.%d\n", i+1)
			if i == MaxRetries-1 {
				return nil, nil, errors.New("max retries reached")
			}
		} else {
			log.Print("Read data failed:", err.Error())
			return nil, nil, err
		}
	}

	return received, bytes_, nil
}
