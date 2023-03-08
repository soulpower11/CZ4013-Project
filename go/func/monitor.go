package functions

import (
	"fmt"
	"log"
	"net"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func MonitorFlight(timeOut int32) {
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

	conn, ip, err := listener()
	if err != nil {
		log.Print("Opening listener failed:", err.Error())
		return
	}
	defer conn.Close()

	send := MonitorRequest{
		FlightId:        utlis.StrToInt32(*flightId),
		MonitorInterval: utlis.StrToInt32(*monitorInterval),
	}
	bytes_, size := utlis.Marshal(send, int32(MONITOR), int32(REQUEST), int32(0), timeOut)
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, bytes_, err := sendToServerAsListener(conn, bytes_, timeOut)
	if err != nil {
		log.Print(err.Error())
		return
	}

	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		interval := time.Duration(utlis.StrToInt32(*monitorInterval)) * time.Minute
		conn.SetReadDeadline(time.Now().Add(interval))

		for start := time.Now(); time.Since(start) < interval; {
			received := make([]byte, 4096)
			_, _, err = conn.ReadFrom(received)

			if err != nil {
				if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
					println("Monitoring ended.")
					break
				} else {
					log.Print("Read data failed:", err.Error())
					return
				}
			}

			_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
			if errorCode == 0 {
				message := response.Value[0].(MonitorResponse).Msg
				fmt.Println(message)
			} else {
				println(response.Error)
				break
			}
		}
	} else {
		println(response.Error)
		return
	}
}
