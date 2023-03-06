package const_

import "time"

type DataType int32

const (
	INT_TYPE DataType = iota
	FLOAT_TYPE
	STRING_TYPE
	TIME_TYPE
)

type ServiceType int32

const (
	QUERY_FLIGHTID ServiceType = iota
	QUERY_DEPARTURETIME
	RESERVATION
	MONITOR
	CHECK_ARRIVALTIME
	CANCALLATION
)

type MessageType int32

const (
	REQUEST MessageType = iota
	REPLY
)

type ByteOrdering int32

const (
	BIG_ENDIAN ByteOrdering = iota
	LITTLE_ENDIAN
)

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

type CheckArrivalTimeRequest struct {
	FlightId int32
}

type CheckArrivalTimeResponse struct {
	ArrivalTime time.Time
}

type CancellationRequest struct {
	FlightId int32
}

type CancellationResponse struct {
	Msg string
}

type Response struct {
	Value []interface{}
	Error string
}
