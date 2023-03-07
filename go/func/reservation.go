package functions

import (
	"fmt"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func Reservation() {
	flightId := utlis.TextPrompt("Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Reservation")
		return
	}

	noOfSeats := utlis.TextPrompt("No. Of Seats:", GetNoOfSeatsValidate())
	if noOfSeats == nil {
		fmt.Println("Exit Reservation")
		return
	}

	conn, ip := connect()
	defer conn.Close()

	send := ReservationRequest{
		FlightId:  utlis.StrToInt32(*flightId),
		NoOfSeats: utlis.StrToInt32(*noOfSeats),
	}
	bytes_, size := utlis.Marshal(send, int32(RESERVATION), int32(REQUEST), int32(0))
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
		println(response.Value[0].(ReservationResponse).Msg)
	} else {
		println(response.Error)
	}
}
