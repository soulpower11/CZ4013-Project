package functions

import (
	"fmt"
	"log"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func QueryFlightId(packetLoss int32) {
	source := utlis.TextPrompt("Source:", GetCountryNameValidate())
	if source == nil {
		fmt.Println("Exit Query Flight Id")
		return
	}

	destination := utlis.TextPrompt("destination:", GetCountryNameValidate())
	if destination == nil {
		fmt.Println("Exit Query Flight Id")
		return
	}

	conn, ip, err := connect()
	if err != nil {
		log.Print("Connecting to server failed:", err.Error())
		return
	}
	defer conn.Close()

	send := QueryFlightIdRequest{
		Source:      *source,
		Destination: *destination,
	}
	bytes_, size := utlis.Marshal(send, int32(QUERY_FLIGHTID), int32(REQUEST), int32(0), packetLoss)
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		flightIds := []int32{}
		for _, res := range response.Value {
			flightIds = append(flightIds, res.(QueryFlightIdResponse).FlightId)
		}
		utlis.DisplayFlightIds(flightIds)
	} else {
		println(response.Error)
	}
}
