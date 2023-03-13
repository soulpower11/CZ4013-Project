package const_

import (
	"time"
)

// Constant values for the server
const (
	// Host = "192.9.175.59"
	Host       = "localhost"
	ClientHost = "localhost"
	Port       = "8080"
	Type       = "udp"
	MaxRetries = 5
	Deadline   = 10 * time.Second
)

//Constant values for the Requests and Responses

type DataType int32

const (
	IntType DataType = iota
	FloatType
	StringType
	TimeType
)

type ServiceType int32

const (
	QueryFlightId_ ServiceType = iota
	QueryDepartureTime_
	Reservation_
	Monitor_
	CheckReservation_
	Cancellation_
)

type MessageType int32

const (
	Request MessageType = iota
	Reply
)

type ByteOrdering int32

const (
	BigEndian ByteOrdering = iota
	LittleEndian
)

// The Request and Response Structs

type QueryFlightIdRequest struct {
	Source      string
	Destination string
}

type QueryFlightIdResponse struct {
	FlightId int32
}

type QueryDepartureTimeRequest struct {
	FlightId int32
}

type QueryDepartureTimeResponse struct {
	DepartureTime    time.Time
	AirFare          float32
	SeatAvailability int32
}

type ReservationRequest struct {
	FlightId  int32
	NoOfSeats int32
}

type ReservationResponse struct {
	Msg string
}

type MonitorRequest struct {
	FlightId        int32
	MonitorInterval int32
}

type MonitorResponse struct {
	Msg string
}

type CheckReservationRequest struct {
	FlightId int32
}

type CheckReservationResponse struct {
	SeatsReserved int32
}

type CancellationRequest struct {
	FlightId int32
}

type CancellationResponse struct {
	Msg string
}

// Response Includes the response struct and the error message
type Response struct {
	Value []interface{}
	Error string
}
