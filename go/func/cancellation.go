package functions

import (
	"fmt"
	"log"
	"time"

	"github.com/jedib0t/go-pretty/text"
	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func Cancellation(packetLoss int32) {
	flightId := utlis.TextPrompt("Enter your Flight ID:", GetFlightIdValidate())
	if flightId == nil {
		fmt.Println("Exit Cancellation")
		return
	}

	conn, ip, err := connect()
	if err != nil {
		log.Print("Connecting to server failed:", err.Error())
		return
	}
	defer conn.Close()

	send := CancellationRequest{
		FlightId: utlis.StrToInt32(*flightId),
	}

	bytes_, size := utlis.Marshal(send, int32(CANCELLATION), int32(REQUEST), int32(0), packetLoss)
	bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

	received, err := sendToServer(conn, bytes_, packetLoss)
	if err != nil {
		log.Print(err.Error())
		return
	}

	_, response, _, errorCode, _ := utlis.Unmarshal(received[23:])
	if errorCode == 0 {
		println(response.Value[0].(CancellationResponse).Msg)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", response.Error))
	}
}
