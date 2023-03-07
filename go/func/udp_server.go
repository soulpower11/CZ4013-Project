package functions

import (
	"fmt"
	"net"
	"os"
)

const (
	HOST = "192.9.175.59"
	// HOST = "localhost"
	PORT = "8080"
	TYPE = "udp"
)

func connect() (*net.UDPConn, string) {
	udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))
	// laddr, err := net.ResolveUDPAddr("udp", "192.168.31.23:8080")

	if err != nil {
		println("ResolveUDPAddr failed:", err.Error())
		os.Exit(1)
	}

	conn, err := net.DialUDP(TYPE, nil, udpServer)
	// conn, err := net.DialUDP(TYPE, laddr, udpServer)
	if err != nil {
		println("Listen failed:", err.Error())
		os.Exit(1)
	}

	localAddr := conn.LocalAddr().(*net.UDPAddr)

	return conn, localAddr.IP.String()
}

func listener() (*net.UDPConn, string) {
	addr := &net.UDPAddr{IP: net.ParseIP("localhost")}
	conn, err := net.ListenUDP(TYPE, addr)
	if err != nil {
		fmt.Printf("Error opening UDP connection: %s", err)
		os.Exit(1)
	}

	localAddr := conn.LocalAddr().(*net.UDPAddr)

	return conn, localAddr.IP.String()
}
