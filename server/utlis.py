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
    flightIds: List[int]
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


def intToByte(num):
    return num.to_bytes(1, byteorder="little")


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
    return int.from_bytes(bytes, byteorder=byteOrder, signed=False)


def bytesToFloat(bytes, byteOrder):
    if byteOrder == ByteOrdering.BIG_ENDIAN:
        return struct.unpack(">f", bytes)[0]
    else:
        return struct.unpack("<f", bytes)[0]


def bytesToString(bytes):
    string = bytes.decode("ascii")
    return string


def bytesToTime(bytes, byteOrder):
    integer = int.from_bytes(bytes, byteorder=byteOrder, signed=False)
    t = time.localtime(integer)
    return t


def toVariable(bytes, dataType, byteOrder):
    if dataType == DataType.INT_TYPE:
        return bytesToInt(bytes, byteOrder)
    elif dataType == DataType.FLOAT_TYPE:
        return bytesToFloat(bytes)
    elif dataType == DataType.STRING_TYPE:
        return bytesToString(bytes)
    elif dataType == DataType.TIME_TYPE:
        return bytesToTime(bytes)


def byteOrderingToByte(num):
    return num.to_bytes(1, byteorder="big")


def byteOrderingFromByte(byte):
    return int.from_bytes(byte, byteorder="big", signed=False)


# Service Type 1 Byte
# Message Type 1 Byte
# Byte Ordering 1 Byte
# Error Code 1 Byte
# No. of element 4 Byte
def addRequestHeader(serviceType, messageType, errorCode, noOfElement, bytes, size):
    resultBytes = bytearray(8 + size)

    serviceBytes = intToByte(serviceType)
    messageBytes = intToByte(messageType)
    byteOrderingBytes = intToByte(getEndianness())
    errorCodeBytes = intToByte(errorCode)
    noOfElementBytes, noOfElementSize = intToBytes(noOfElement)

    resultBytes[0:1] = serviceBytes
    resultBytes[1:2] = messageBytes
    resultBytes[2:3] = byteOrderingBytes
    resultBytes[3:4] = errorCodeBytes
    resultBytes[4 : 4 + noOfElementSize] = noOfElementBytes
    resultBytes[8 : 8 + size] = bytes[:size]

    return resultBytes, 8 + size


# Length of Element 4 Byte
def addElementHeader(length, bytes, size):
    resultBytes = bytearray(4 + size)

    lengtBytes, lengthSize = intToBytes(length)
    resultBytes[0 : 0 + lengthSize] = lengtBytes
    resultBytes[4 : 4 + size] = bytes[:size]

    return resultBytes, 4 + size


# Data Type 1 Byte
# Length of variable 4 Byte
def addVariableHeader(dataType, length, bytes, size):
    resultBytes = bytearray(5 + size)

    dataTypeBytes = intToByte(dataType)
    lengtBytes, lengthSize = intToBytes(length)

    resultBytes[0:1] = dataTypeBytes
    resultBytes[1 : 1 + lengthSize] = lengtBytes
    resultBytes[5 : 5 + size] = bytes[:size]

    return resultBytes, 5 + size


def setField(dataClass, index, value, serviceType, messageType):
    if serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REQUEST:
        if index == 0:
            dataClass.source = value
        elif index == 1:
            dataClass.destination = value


# 8 Bytes Request Header
# 4 Bytes Element Header
# 5 Bytes Variable Header
def unmarshal(bytesStr):
    requestHeader = bytesStr[:8]

    byteOrdering = (
        "big"
        if byteOrderingFromByte(requestHeader[2:3]) == ByteOrdering.BIG_ENDIAN
        else "little"
    )
    serviceType = bytesToInt(requestHeader[0:1], byteOrdering)
    messageType = bytesToInt(requestHeader[1:2], byteOrdering)
    errorCode = bytesToInt(requestHeader[3:4], byteOrdering)
    noOfElement = bytesToInt(requestHeader[4:], byteOrdering)

    elementsByte = bytesStr[8:]

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


def marshal(r, serviceType, messageType, errorCode):
    if serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REQUEST:
        sourceBytes, sourceSize = stringToBytes(r.source)
        sourceBytes, sourceSize = addVariableHeader(
            DataType.STRING_TYPE, sourceSize, sourceBytes, sourceSize
        )

        destinationBytes, destinationSize = stringToBytes(r.destination)
        destinationBytes, destinationSize = addVariableHeader(
            DataType.STRING_TYPE, destinationSize, destinationBytes, destinationSize
        )

        resultSize = sourceSize + destinationSize
        resultBytes = bytearray(resultSize)

        resultBytes[0:sourceSize] = sourceBytes
        resultBytes[sourceSize : sourceSize + destinationSize] = destinationBytes
        resultBytes, resultSize = addElementHeader(resultSize, resultBytes, resultSize)

        bytes, size = addRequestHeader(
            serviceType, messageType, errorCode, 1, resultBytes, resultSize
        )

        return bytes, size
    elif serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REPLY:
        length = len(r.flightIds)
        resultSize = 0
        resultBytes = bytearray()
        for flightId in r.flightIds:
            flightIdBytes, flightIdSize = intToBytes(flightId)
            flightIdBytes, flightIdSize = addVariableHeader(
                DataType.INT_TYPE, flightIdSize, flightIdBytes, flightIdSize
            )
            flightIdBytes, flightIdSize = addElementHeader(
                flightIdSize, flightIdBytes, flightIdSize
            )

            resultSize += flightIdSize
            resultBytes.extend(flightIdBytes)

        bytes, size = addRequestHeader(
            serviceType, messageType, errorCode, length, resultBytes, resultSize
        )

        return bytes, size
