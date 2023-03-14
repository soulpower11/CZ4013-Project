package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4013-Project/const"
	"github.com/soulpower11/CZ4013-Project/utlis"
)

// Reservation The reservation function
// Reserve seats for a specific Flight ID
func Reservation(packetLoss int32) {
	// Get the input for the Flight ID
	flightId := utlis.TextPrompt("Enter the Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit _Reservation")
		return
	}

	// Get the input for the No. of Seats
	noOfSeats := utlis.TextPrompt("Enter the No. Of Seats:", GetNoOfSeatsValidate())
	if noOfSeats == nil {
		fmt.Println("Exit _Reservation")
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
	send := ReservationRequest{
		FlightId:  utlis.StrToInt32(*flightId),
		NoOfSeats: utlis.StrToInt32(*noOfSeats),
	}
	// Marshal the request message into bytes
	bytes_, size := utlis.Marshal(send, int32(Reservation_), int32(Request), int32(0), packetLoss)
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
		fmt.Printf("%s\n", text.FgGreen.Sprintf("%s", response.Value[0].(ReservationResponse).Msg))
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
