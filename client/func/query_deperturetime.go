package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// QueryDepartureTime The query flight details feature
// Get the departure time, airfare and seat availability of a specific Flight ID
func QueryDepartureTime(packetLoss int32) {
	// Get the input for the Flight ID
	flightId := utlis.TextPrompt("Enter the Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Query Departure Time")
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
	send := QueryDepartureTimeRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}
	// Marshal the request message into bytes
	bytes_, size := utlis.Marshal(send, int32(QueryDepartureTime_), int32(Request), int32(0), packetLoss)
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
		flightInfos := make([]QueryDepartureTimeResponse, len(response.Value))

		for i, res := range response.Value {
			flightInfos[i].DepartureTime = res.(QueryDepartureTimeResponse).DepartureTime
			flightInfos[i].AirFare = res.(QueryDepartureTimeResponse).AirFare
			flightInfos[i].SeatAvailability = res.(QueryDepartureTimeResponse).SeatAvailability
		}
		utlis.DisplayFlightInfo(flightInfos)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
