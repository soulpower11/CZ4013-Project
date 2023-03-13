package functions

import (
	"fmt"
	"log"
	"net"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// MonitorFlight The monitor feature
// Monitor the seats availability of a specific flight
func MonitorFlight(packetLoss int32) {
	// Get the input for the Flight ID
	flightId := utlis.TextPrompt("Enter the Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Monitor Flight")
		return
	}

	// Get the input for the Monitor Interval
	monitorInterval := utlis.TextPrompt("Enter the Monitor Interval (In Mins):", GetMonitorIntervalValidate())
	if flightId == nil {
		fmt.Println("Exit Monitor Flight")
		return
	}

	// Create a listener
	conn, ip, err := listener()
	if err != nil {
		log.Print("Opening listener failed:", err.Error())
		return
	}
	defer conn.Close()

	// Set the request message
	send := MonitorRequest{
		FlightId:        utlis.StrToInt32(*flightId),
		MonitorInterval: utlis.StrToInt32(*monitorInterval),
	}
	// Marshal the request message into bytes
	bytes_, size := utlis.Marshal(send, int32(Monitor_), int32(Request), int32(0), packetLoss)
	// Add the request ID into the bytes
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	// Send the request to the server and get the response or the error
	received, bytes_, err := sendToServerAsListener(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	// Unmarshal the response into a struct
	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		// Print out the success message if there is no error
		message := response.Value[0].(MonitorResponse).Msg
		fmt.Println(message)

		// Set the response timeout to the monitor interval
		interval := time.Duration(utlis.StrToInt32(*monitorInterval)) * time.Minute
		conn.SetReadDeadline(time.Now().Add(interval))

		// Start a loop that will end when the monitor interval ends
		for start := time.Now(); time.Since(start) < interval; {
			received := make([]byte, 4096)
			_, _, err = conn.ReadFrom(received)

			if err != nil {
				// If the error is the timeout error. It means the monitoring have ended
				if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
					println("Monitoring ended.")
					break
				} else {
					log.Print("Read data failed:", err.Error())
					return
				}
			}

			// Unmarshal the response into a struct
			_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
			if errorCode == 0 {
				message := response.Value[0].(MonitorResponse).Msg
				fmt.Println(message)
			} else {
				fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
				break
			}
		}
	} else {
		// Print out the error if there is any
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
		return
	}
}
