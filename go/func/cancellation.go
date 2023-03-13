package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// Cancellation The cancellation feature
// Cancel the seat reservation of a specific Flight ID
func Cancellation(packetLoss int32) {
	// Get the input for the Flight ID
	flightId := utlis.TextPrompt("Enter your Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Cancellation")
		return
	}

	// Create a connection to the server
	conn, ip, err := connect()
	if err != nil {
		log.Print("Connecting to server failed:", err.Error())
		return
	}
	defer conn.Close()

	// Set the request message
	send := CancellationRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}

	// Marshal the request message into bytes
	bytes_, size := utlis.Marshal(send, int32(Cancellation_), int32(Request), int32(0), packetLoss)
	// Add the request ID into the bytes
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	// Send the request to the server and get the response or the error
	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	// Unmarshal the response into a struct
	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		println(response.Value[0].(CancellationResponse).Msg)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
