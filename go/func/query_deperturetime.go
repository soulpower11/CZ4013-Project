package functions

import (
	"fmt"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func QueryDepartureTime() {
	flightId := utlis.TextPrompt("Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Query Departure Time")
		return
	}

	conn, ip := connect()
	defer conn.Close()

	send := QueryDepartureTimeRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}
	bytes_, size := utlis.Marshal(send, int32(QUERY_DEPARTURETIME), int32(REQUEST), int32(0))
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
		flightInfos := make([]QueryDepartureTimeResponse, len(response.Value))

		for i, res := range response.Value {
			flightInfos[i].DepartureTime = res.(QueryDepartureTimeResponse).DepartureTime
			flightInfos[i].AirFare = res.(QueryDepartureTimeResponse).AirFare
			flightInfos[i].SeatAvailability = res.(QueryDepartureTimeResponse).SeatAvailability
		}
		utlis.DisplayFlightInfo(flightInfos)
	} else {
		println(response.Error)
	}
}