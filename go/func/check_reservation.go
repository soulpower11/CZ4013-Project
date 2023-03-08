package functions

import (
	"fmt"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func CheckReservation(on int) {
	flightId := utlis.TextPrompt("Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Check Reservation")
		return
	}

	conn, ip := connect()
	defer conn.Close()

	send := CheckReservationRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}
	bytes_, size := utlis.Marshal(send, int32(CHECK_RESERVATION), int32(REQUEST), int32(on), int32(0))
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
		// SeatsReserved := []int32{}
		// for _, res := range response.Value {
		// 	SeatsReserved = append(SeatsReserved, res.(CheckReservationResponse).SeatsReserved)
		// }
		// utlis.DisplaySeatsReserved(SeatsReserved)
		seatsReserved := response.Value[0].(CheckReservationResponse).SeatsReserved
		fmt.Printf("%d seats is reserved for Flight ID %s\n", seatsReserved, *flightId)
	} else {
		println(response.Error)
	}
}
