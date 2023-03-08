package functions

import (
	"fmt"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

var MAX_RETRIES = 5
var TIMEOUT = 2 //Seconds

func QueryFlightId(on int) {
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

	for retries := 0; retries < MAX_RETRIES; retries++ {
		send := QueryFlightIdRequest{
			Source:      *source,
			Destination: *destination,
		}
		bytes_, size := utlis.Marshal(send, int32(QUERY_FLIGHTID), int32(REQUEST), int32(on), int32(0))
		bytes_, size = utlis.AddRequestID(ip, time.Now(), bytes_, size)

		_, err := conn.Write(bytes_)
		if err != nil {
			println("Write data failed:", err.Error())
			os.Exit(1)
		}

		responses := make(chan []byte)
		go func() {
			received := make([]byte, 1024)
			_, err := conn.Read(received)
			if err != nil {
				println("Read data failed:", err.Error())
				responses <- nil
			} else {
				responses <- received
			}
		}()

		select {
		case received := <-responses:
			if received == nil {
				fmt.Printf("Error reading data from server. Retrying request %d...\n", retries+1)
				continue
			}
			_, response, _, errorCode := utlis.Unmarshal(received[20:])
			if errorCode == 0 {
				flightIds := []int32{}
				for _, res := range response.Value {
					flightIds = append(flightIds, res.(QueryFlightIdResponse).FlightId)
				}
				utlis.DisplayFlightIds(flightIds)
				return
			} else {
				println(response.Error)
				fmt.Printf("Retrying request %d...\n", retries+1)
			}
		case <-time.After(time.Duration(TIMEOUT) * time.Second):
			fmt.Printf("Timeout occurred while waiting for server response. Retrying request %d...\n", retries+1)
		}
	}
	fmt.Printf("Exceeded maximum number of retries. Exiting Query Flight Id.\n")
}
