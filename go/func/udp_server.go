package functions

import (
	"errors"
	"fmt"
	"log"
	"net"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func getClientIp() (string, error) {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return "", err
	}
	for _, addr := range addrs {
		ipnet, ok := addr.(*net.IPNet)
		if ok && !ipnet.IP.IsLoopback() && ipnet.IP.To4() != nil {
			return ipnet.IP.String(), nil
		}
	}
	return "", errors.New("IP not found")
}

func connect() (*net.UDPConn, string, error) {
	udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))
	if err != nil {
		log.Print("ResolveUDPAddr failed:", err.Error())
		return nil, "", err
	}

	conn, err := net.DialUDP(TYPE, nil, udpServer)
	if err != nil {
		log.Print("Listen failed:", err.Error())
		return nil, "", err
	}

	localAddr := conn.LocalAddr().(*net.UDPAddr)

	return conn, localAddr.IP.String(), nil
}

func listener() (*net.UDPConn, string, error) {
	addr := &net.UDPAddr{IP: net.ParseIP(CLIENTHOST)}
	conn, err := net.ListenUDP(TYPE, addr)
	if err != nil {
		log.Print("Error opening UDP connection:", err)
		return nil, "", err
	}

	// udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))
	// if err != nil {
	// 	log.Print("ResolveUDPAddr failed:", err.Error())
	// 	return nil, "", err
	// }

	// conn2, err := net.DialUDP(TYPE, nil, udpServer)
	// if err != nil {
	// 	log.Print("Listen failed:", err.Error())
	// 	return nil, "", err
	// }
	// defer conn2.Close()
	// localAddr := conn2.LocalAddr().(*net.UDPAddr)

	// return conn, localAddr.IP.String(), nil

	ip, _ := getClientIp()
	return conn, ip, nil
}

func sendToServer(conn *net.UDPConn, bytes_ []byte, timeOut int32) ([]byte, error) {
	var received []byte
	for i := 0; i < MAXRETRIES; i++ {
		if i == 4 {
			bytes_ = utlis.TurnTimeOutOff(bytes_)
		}

		_, err := conn.Write(bytes_)
		if err != nil {
			log.Print("Write data failed:", err.Error())
			return nil, err
		}

		conn.SetReadDeadline(time.Now().Add(DEADLINE))
		received = make([]byte, 4096)
		_, err = conn.Read(received)
		if err == nil {
			break
		}

		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			fmt.Printf("Retrying No. %d\n", i+1)
			if i == MAXRETRIES-1 {
				return nil, errors.New("Max retries reached!")
			}
		} else {
			log.Print("Read data failed:", err.Error())
			return nil, err
		}
	}

	return received, nil
}

func sendToServerAsListener(conn *net.UDPConn, bytes_ []byte, timeOut int32) ([]byte, []byte, error) {
	var received []byte

	udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))
	if err != nil {
		log.Print("ResolveUDPAddr failed:", err.Error())
		return nil, nil, err
	}
	for i := 0; i < MAXRETRIES; i++ {
		if i == 4 {
			bytes_ = utlis.TurnTimeOutOff(bytes_)
		}

		_, err := conn.WriteToUDP(bytes_, udpServer)
		if err != nil {
			log.Print("Write data failed:", err.Error())
			return nil, nil, err
		}

		conn.SetReadDeadline(time.Now().Add(DEADLINE))
		received = make([]byte, 4096)
		_, _, err = conn.ReadFrom(received)
		if err == nil {
			break
		}

		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			fmt.Printf("Retrying No. %d\n", i+1)
			if i == MAXRETRIES-1 {
				return nil, nil, errors.New("Max retries reached!")
			}
		} else {
			log.Print("Read data failed:", err.Error())
			return nil, nil, err
		}
	}

	return received, bytes_, nil
}
