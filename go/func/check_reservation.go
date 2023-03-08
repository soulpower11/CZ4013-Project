package functions

import (
	"fmt"
	"log"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func CheckReservation(packetLoss int32) {
	flightId := utlis.TextPrompt("Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Check Reservation")
		return
	}

	conn, ip, err := connect()
	if err != nil {
		log.Print("Connecting to server failed:", err.Error())
		return
	}
	defer conn.Close()

	send := CheckReservationRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}
	bytes_, size := utlis.Marshal(send, int32(CHECK_RESERVATION), int32(REQUEST), int32(0), packetLoss)
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		seatsReserved := response.Value[0].(CheckReservationResponse).SeatsReserved
		fmt.Printf("%d seats is reserved for Flight ID %s\n", seatsReserved, *flightId)
	} else {
		println(response.Error)
	}
}
