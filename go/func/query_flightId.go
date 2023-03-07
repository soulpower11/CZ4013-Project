package functions

import (
	"fmt"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func QueryFlightId() {
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

	conn, ip := connect()
	defer conn.Close()

	send := QueryFlightIdRequest{
		Source:      *source,
		Destination: *destination,
	}
	bytes_, size := utlis.Marshal(send, int32(QUERY_FLIGHTID), int32(REQUEST), int32(0))
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	_, err := conn.Write(bytes_)
	if err != nil {
		println("Write data failed:", err.Error())
		os.Exit(1)
	}

	received := make([]byte, 1024)
	_, err = conn.Read(received)

	if err != nil {
		println("Read data failed:", err.Error())
		os.Exit(1)
	}

	_, response, _, errorCode := utlis.Unmarshal(received[20:])
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
