package main

import (
	"log"
	"net"
	"os"
	"time"

	. "github.com/soulpower11/CZ4031-Project/const"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

const (
	HOST = "localhost"
	PORT = "8080"
	TYPE = "tcp"
)

func main() {
	udpServer, err := net.ResolveUDPAddr("udp", ":8080")

	if err != nil {
		println("ResolveUDPAddr failed:", err.Error())
		os.Exit(1)
	}

	conn, err := net.DialUDP("udp", nil, udpServer)
	if err != nil {
		println("Listen failed:", err.Error())
		os.Exit(1)
	}

	//close the connection
	defer conn.Close()

	send := QueryFlightIdRequest{
		Source:      "Taiwan",
		Destination: "Hong Kong",
	}

	bytes_, size := utlis.Marshal(send, int32(QUERY_FLIGHTID), int32(REQUEST), int32(0))
	bytes_, size = utlis.AddRequestID("192.168.1.1", time.Now(), bytes_, size)

	_, err = conn.Write(bytes_)
	// _, err = conn.Write([]byte("This is a UDP message"))
	if err != nil {
		println("Write data failed:", err.Error())
		os.Exit(1)
	}

	// buffer to get data
	received := make([]byte, 1024)
	_, err = conn.Read(received)

	if err != nil {
		println("Read data failed:", err.Error())
		os.Exit(1)
	}

	request, _ := utlis.Unmarshal(received[20:])
	re, ok := request[0].(ReservationRequest)

	log.Println(ok)
	log.Println(re.FlightId)
	log.Println(re.NoOfSeats)

	// _, response := utlis.Unmarshal(received[20:])

	// log.Println(len(response.Value))
	// for _, res := range response.Value {
	// 	r := res.(QueryDepartureTimeResponse)
	// 	log.Print("The Departure Time is ", r.DepartureTime)
	// 	log.Print("The Air Fare is ", r.AirFare)
	// 	log.Print("The Seat Availability is ", r.SeatAvailability)
	// }

	// request, _ := utlis.Unmarshal(received[20:])
	// re, ok := request[0].(QueryDepartureTimeRequest)

	// log.Println(ok)
	// log.Println(re.FlightId)
	// log.Println(re.Destination)

	// for _, response := range r.(Response).Value {
	// 	log.Print("The Flight ID is ", response.(QueryFlightIdResponse).FlightId)
	// }
	// println(r)

	// println(string(received))
}
