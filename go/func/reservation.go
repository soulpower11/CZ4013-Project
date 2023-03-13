package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func Reservation(packetLoss int32) {
	flightId := utlis.TextPrompt("Enter the Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Reservation")
		return
	}

	noOfSeats := utlis.TextPrompt("Enter the No. Of Seats:", GetNoOfSeatsValidate())
	if noOfSeats == nil {
		fmt.Println("Exit Reservation")
		return
	}

	conn, ip, err := connect()
	if err != nil {
		log.Print("Connecting to server failed:", err.Error())
		return
	}
	defer conn.Close()

	send := ReservationRequest{
		FlightId:  utlis.StrToInt32(*flightId),
		NoOfSeats: utlis.StrToInt32(*noOfSeats),
	}
	bytes_, size := utlis.Marshal(send, int32(RESERVATION), int32(REQUEST), int32(0), packetLoss)
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		println(response.Value[0].(ReservationResponse).Msg)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
