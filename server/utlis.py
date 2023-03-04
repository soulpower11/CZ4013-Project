import struct
import time
from typing import List
from dataclasses import dataclass
import string
from enum import IntEnum
import sys


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
    source: string
    destination: string


@dataclass
class QueryFlightIdResponse:
    flightId: List[int]
    error: string


@dataclass
class QueryDepartureTimeRequest:
    flightId: int


@dataclass
class QueryDepartureTimeResponse:
    departureTime: time.struct_time
    airFare: float
    seatAvailability: int
    error: string


@dataclass
class ReservationRequest:
    flightId: int
    noOfSeats: int


@dataclass
class ReservationResponse:
    msg: string
    error: string


@dataclass
class MonitorRequest:
    flightId: int
    monitorInterval: int


@dataclass
class MonitorResponse:
    msg: string
    error: string


@dataclass
class CheckArrivalTimeRequest:
    flightId: int


@dataclass
class CheckArrivalTimeResponse:
    arrivalTime: time.struct_time
    error: string


@dataclass
class CancellationRequest:
    flightId: int


@dataclass
class CancellationResponse:
    msg: string
    error: string


def getEndianness():
    if sys.byteorder == "little":
        return ByteOrdering.LITTLE_ENDIAN
    else:
        return ByteOrdering.BIG_ENDIAN


def intToBytes(num):
    size = struct.calcsize("i")
    bytes = struct.pack("i", num)
    return bytes, size


def floatToBytes(num):
    size = struct.calcsize("f")
    bytes = struct.pack("f", num)
    return bytes, size


def stringToBytes(string):
    bytes = string.encode("ascii")
    size = len(bytes)
    return bytes, size


def timeToBytes(time):
    size = struct.calcsize("Q")
    bytes = struct.pack("Q", time)
    return bytes, size


def toBytes(variable):
    if type(variable) == int:
        return intToBytes(variable)
    elif type(variable) == float:
        return floatToBytes(variable)
    elif type(variable) == str:
        return stringToBytes(variable)
    elif type(variable) == string:
        return stringToBytes(variable)
    elif type(variable) == time.struct_time:
        return timeToBytes(variable)


def bytesToInt(bytes, byteOrder):
    integer = int.from_bytes(bytes, byteorder=byteOrder, signed=False)
    return integer


def bytesToString(bytes):
    string = bytes.decode("ascii")
    return string


def toVariable(bytes, dataType, byteOrder):
    if dataType == DataType.INT_TYPE:
        return bytesToInt(bytes, byteOrder)
    elif dataType == DataType.STRING_TYPE:
        return bytesToString(bytes)


def setField(dataClass, index, value, serviceType, messageType):
    if serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REQUEST:
        if index == 0:
            dataClass.source = value
        elif index == 1:
            dataClass.destination = value


# 7 Bytes Request Header
# 4 Bytes Element Header
# 5 Bytes Variable Header


def unmarshal(bytesStr):
    requestHeader = bytesStr[:7]

    byteOrdering = "big" if requestHeader[2:3] == ByteOrdering.BIG_ENDIAN else "little"
    serviceType = bytesToInt(requestHeader[0:1], byteOrdering)
    messageType = bytesToInt(requestHeader[1:2], byteOrdering)
    noOfElement = bytesToInt(requestHeader[3:], byteOrdering)

    elementsByte = bytesStr[7:]

    if serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REQUEST:
        queryRequest = [QueryFlightIdRequest("", "") for i in range(noOfElement)]
        for i in range(noOfElement):
            lengthOfElement = bytesToInt(elementsByte[:4], byteOrdering)
            variablesByte = elementsByte[4 : 4 + lengthOfElement]
            elementsByte = elementsByte[4 + lengthOfElement :]

            index = 0
            while len(variablesByte) != 0:
                variableHeader = variablesByte[:5]
                dataType = bytesToInt(variableHeader[0:1], byteOrdering)
                lengthOfVariable = bytesToInt(variableHeader[1:], byteOrdering)
                variableByte = variablesByte[5 : 5 + lengthOfVariable]
                setField(
                    queryRequest[i],
                    index,
                    toVariable(variableByte, dataType, byteOrdering),
                    serviceType,
                    messageType,
                )
                variablesByte = variablesByte[5 + lengthOfVariable :]

                index += 1

        return queryRequest
