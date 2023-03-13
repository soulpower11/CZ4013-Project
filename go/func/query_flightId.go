package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// QueryFlightId The query Flight ID feature
// Get the Flight IDs by specifying the source and destination country
func QueryFlightId(packetLoss int32) {
	// Get the input for the source country
	source := utlis.TextPrompt("Enter the source country:", GetCountryNameValidate())
	if source == nil {
		fmt.Println("Exit Query Flight Id")
		return
	}

	// Get the input for the destination country
	destination := utlis.TextPrompt("Enter the destination country:", GetCountryNameValidate())
	if destination == nil {
		fmt.Println("Exit Query Flight Id")
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
	send := QueryFlightIdRequest{
		Source:      *source,
		Destination: *destination,
	}
	// Marshal the request message into bytes
	bytes_, size := utlis.Marshal(send, int32(QueryFlightId_), int32(Request), int32(0), packetLoss)
	// Add the request ID into the bytes
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	// Unmarshal the response into a struct
	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		var flightIds []int32
		for _, res := range response.Value {
			flightIds = append(flightIds, res.(QueryFlightIdResponse).FlightId)
		}
		utlis.DisplayFlightIds(flightIds)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
