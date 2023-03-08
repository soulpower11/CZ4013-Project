package functions

import (
	"fmt"
	"net"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func MonitorFlight(on int) {
	flightId := utlis.TextPrompt("Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Monitor Flight")
		return
	}

	monitorInterval := utlis.TextPrompt("Monitor Interval (In Mins):", GetMonitorIntervalValidate())
	if flightId == nil {
		fmt.Println("Exit Monitor Flight")
		return
	}

	conn, ip := listener()
	defer conn.Close()

	send := MonitorRequest{
		FlightId:        utlis.StrToInt32(*flightId),
		MonitorInterval: utlis.StrToInt32(*monitorInterval),
	}
	bytes_, size := utlis.Marshal(send, int32(MONITOR), int32(REQUEST), int32(on), int32(0))
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	// _, err := conn.Write(bytes_)
	udpServer, err := net.ResolveUDPAddr(TYPE, fmt.Sprintf("%s:%s", HOST, PORT))
	_, err = conn.WriteToUDP(bytes_, udpServer)

	if err != nil {
		println("Write data failed:", err.Error())
		os.Exit(1)
	}

	timeOut := time.Duration(utlis.StrToInt32(*monitorInterval)) * time.Minute
	conn.SetReadDeadline(time.Now().Add(timeOut))

	for start := time.Now(); time.Since(start) < timeOut; {
		received := make([]byte, 4096)
		_, _, err = conn.ReadFrom(received)

		if err != nil {
			if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
				// println("Timeout error:", err)
				println("Monitoring ended.")
				break
			} else {
				println("Read data failed:", err.Error())
				os.Exit(1)
			}
		}

		_, response, _, errorCode := utlis.Unmarshal(received[20:])
		if errorCode == 0 {
			message := response.Value[0].(MonitorResponse).Msg
			fmt.Println(message)
		} else {
			println(response.Error)
			break
		}
	}

}
