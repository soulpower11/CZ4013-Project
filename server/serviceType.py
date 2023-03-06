from typing import Union
import time
from typing import List, Optional
from dataclasses import dataclass
from enum import IntEnum


class DataType(IntEnum):
    INT_TYPE = 0
    FLOAT_TYPE = 1
    STRING_TYPE = 2
    TIME_TYPE = 3


class ServiceType(IntEnum):
    QUERY_FLIGHTID = 0
    QUERY_DEPARTURETIME = 1
    RESERVATION = 2
    MONITOR = 3
    CHECK_ARRIVALTIME = 4
    CANCALLATION = 5


class MessageType(IntEnum):
    REQUEST = 0
    REPLY = 1


class ByteOrdering(IntEnum):
    BIG_ENDIAN = 0
    LITTLE_ENDIAN = 1


@dataclass
class QueryFlightIdRequest:
    source: Optional[str] = None
    destination: Optional[str] = None


@dataclass
class QueryFlightIdResponse:
    flightId: Optional[int] = None


@dataclass
class QueryDepartureTimeRequest:
    flightId: Optional[int] = None


@dataclass
class QueryDepartureTimeResponse:
    departureTime: Optional[time.struct_time] = None
    airFare: Optional[float] = None
    seatAvailability: Optional[int] = None


@dataclass
class ReservationRequest:
    flightId: Optional[int] = None
    noOfSeats: Optional[int] = None


@dataclass
class ReservationResponse:
    msg: Optional[str] = None


@dataclass
class MonitorRequest:
    flightId: Optional[int] = None
    monitorInterval: Optional[int] = None


@dataclass
class MonitorResponse:
    msg: Optional[str] = None


@dataclass
class CheckArrivalTimeRequest:
    flightId: Optional[int] = None


@dataclass
class CheckArrivalTimeResponse:
    arrivalTime: Optional[time.struct_time] = None


@dataclass
class CancellationRequest:
    flightId: Optional[int] = None


@dataclass
class CancellationResponse:
    msg: Optional[str] = None


@dataclass
class Response:
    value: Union[
        List[QueryFlightIdResponse],
        List[QueryDepartureTimeResponse],
        List[ReservationResponse],
        List[MonitorResponse],
        List[CheckArrivalTimeResponse],
        List[CancellationResponse],
        None,
    ] = None
    error: Optional[str] = None
