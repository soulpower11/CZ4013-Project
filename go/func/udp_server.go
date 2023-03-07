package functions

import (
	"fmt"
	"net"
	"os"
)

const (
	HOST = "localhost"
	PORT = "8080"
	TYPE = "udp"
)

func connect() (*net.UDPConn, string) {
	udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))

	if err != nil {
		println("ResolveUDPAddr failed:", err.Error())
		os.Exit(1)
	}

	conn, err := net.DialUDP(TYPE, nil, udpServer)
	if err != nil {
		println("Listen failed:", err.Error())
		os.Exit(1)
	}

	localAddr := conn.LocalAddr().(*net.UDPAddr)

	return conn, localAddr.IP.String()
}
