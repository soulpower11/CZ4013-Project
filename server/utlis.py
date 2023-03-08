import struct
import time
from dataclasses import dataclass, fields
import string
import sys
from serviceType import (
    ByteOrdering,
    DataType,
    ServiceType,
    MessageType,
    QueryFlightIdResponse,
    QueryFlightIdRequest,
    QueryDepartureTimeResponse,
    QueryDepartureTimeRequest,
    CancellationRequest,
    CancellationResponse,
    CheckReservationRequest,
    CheckReservationResponse,
    MonitorRequest,
    MonitorResponse,
    ReservationRequest,
    ReservationResponse,
    Response,
)


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


def timeToBytes(structTime):
    size = struct.calcsize("Q")
    bytes = struct.pack("Q", int(time.mktime(structTime)))
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
        return bytesToFloat(bytes, byteOrder)
    elif dataType == DataType.STRING_TYPE:
        return bytesToString(bytes)
    elif dataType == DataType.TIME_TYPE:
        return bytesToTime(bytes, byteOrder)


def byteOrderingToByte(num):
    return num.to_bytes(1, byteorder="big")


def byteOrderingFromByte(byte):
    return int.from_bytes(byte, byteorder="big", signed=False)


def getDataType(variable):
    if type(variable) == int:
        return DataType.INT_TYPE
    elif type(variable) == float:
        return DataType.FLOAT_TYPE
    elif type(variable) == str:
        return DataType.STRING_TYPE
    elif type(variable) == string:
        return DataType.STRING_TYPE
    elif type(variable) == time.struct_time:
        return DataType.TIME_TYPE


# IP+Time 20 Bytes
def addRequestID(ip, time, bytes, size):
    resultBytes = bytearray(20 + size)

    ipBytes, ipSize = toBytes(ip)
    timeBytes, timeSize = toBytes(time)

    resultBytes[0:ipSize] = ipBytes
    resultBytes[ipSize : ipSize + timeSize] = timeBytes
    resultBytes[20 : 20 + size] = bytes[:size]

    return resultBytes, 20 + size


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
    noOfElementBytes, noOfElementSize = toBytes(noOfElement)

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

    lengtBytes, lengthSize = toBytes(length)
    resultBytes[0 : 0 + lengthSize] = lengtBytes
    resultBytes[4 : 4 + size] = bytes[:size]

    return resultBytes, 4 + size


# Data Type 1 Byte
# Length of variable 4 Byte
def addVariableHeader(dataType, length, bytes, size):
    resultBytes = bytearray(5 + size)

    dataTypeBytes = intToByte(dataType)
    lengtBytes, lengthSize = toBytes(length)

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
    elif serviceType == ServiceType.QUERY_FLIGHTID and messageType == MessageType.REPLY:
        if index == 0:
            dataClass.flightId = value
    elif (
        serviceType == ServiceType.QUERY_DEPARTURETIME
        and messageType == MessageType.REQUEST
    ):
        if index == 0:
            dataClass.flightId = value
    elif (
        serviceType == ServiceType.QUERY_DEPARTURETIME
        and messageType == MessageType.REPLY
    ):
        if index == 0:
            dataClass.departureTime = value
        elif index == 1:
            dataClass.airFare = value
        elif index == 2:
            dataClass.seatAvailability = value
    elif serviceType == ServiceType.RESERVATION and messageType == MessageType.REQUEST:
        if index == 0:
            dataClass.flightId = value
        elif index == 1:
            dataClass.noOfSeats = value
    elif serviceType == ServiceType.RESERVATION and messageType == MessageType.REPLY:
        if index == 0:
            dataClass.msg = value
    elif serviceType == ServiceType.MONITOR and messageType == MessageType.REQUEST:
        if index == 0:
            dataClass.flightId = value
        elif index == 1:
            dataClass.monitorInterval = value
    elif serviceType == ServiceType.MONITOR and messageType == MessageType.REPLY:
        if index == 0:
            dataClass.msg = value
    elif (
        serviceType == ServiceType.CHECK_RESERVATION
        and messageType == MessageType.REQUEST
    ):
        if index == 0:
            dataClass.flightId = value
    elif (
        serviceType == ServiceType.CHECK_RESERVATION
        and messageType == MessageType.REPLY
    ):
        if index == 0:
            dataClass.seatsReserved = value
    elif serviceType == ServiceType.CANCELLATION and messageType == MessageType.REQUEST:
        if index == 0:
            dataClass.flightId = value
    elif serviceType == ServiceType.CANCELLATION and messageType == MessageType.REPLY:
        if index == 0:
            dataClass.msg = value

    return dataClass


def decodeRequestHeader(requestHeader):
    byteOrdering = (
        "big"
        if byteOrderingFromByte(requestHeader[2:3]) == ByteOrdering.BIG_ENDIAN
        else "little"
    )
    serviceType = bytesToInt(requestHeader[0:1], byteOrdering)
    messageType = bytesToInt(requestHeader[1:2], byteOrdering)
    errorCode = bytesToInt(requestHeader[3:4], byteOrdering)
    on_off = bytesToInt(requestHeader[4:5], byteOrdering)
    noOfElement = bytesToInt(requestHeader[5:], byteOrdering)

    return byteOrdering, serviceType, messageType, errorCode, on_off, noOfElement


def decodeElementHeader(elementsByte, byteOrdering):
    lengthOfElement = bytesToInt(elementsByte[:4], byteOrdering)
    variablesByte = elementsByte[4 : 4 + lengthOfElement]

    return lengthOfElement, variablesByte


def decodeVariableHeader(variableHeader, byteOrdering):
    dataType = bytesToInt(variableHeader[0:1], byteOrdering)
    lengthOfVariable = bytesToInt(variableHeader[1:], byteOrdering)

    return dataType, lengthOfVariable


def decodeQuery(
    query, elementsByte, byteOrdering, noOfElement, serviceType, messageType
):
    for i in range(noOfElement):
        lengthOfElement, variablesByte = decodeElementHeader(elementsByte, byteOrdering)
        elementsByte = elementsByte[4 + lengthOfElement :]

        index = 0
        while len(variablesByte) != 0:
            variableHeader = variablesByte[:5]
            dataType, lengthOfVariable = decodeVariableHeader(
                variableHeader, byteOrdering
            )

            variableByte = variablesByte[5 : 5 + lengthOfVariable]
            query[i] = setField(
                query[i],
                index,
                toVariable(variableByte, dataType, byteOrdering),
                serviceType,
                messageType,
            )

            variablesByte = variablesByte[5 + lengthOfVariable :]
            index += 1

    return query


def decodeError(queryResponse, elementsByte, byteOrdering):
    lengthOfElement, variablesByte = decodeElementHeader(elementsByte, byteOrdering)
    elementsByte = elementsByte[4 + lengthOfElement :]

    variableHeader = variablesByte[:5]
    dataType, lengthOfVariable = decodeVariableHeader(variableHeader, byteOrdering)
    variableByte = variablesByte[5 : 5 + lengthOfVariable]

    queryResponse.error = toVariable(variableByte, dataType, byteOrdering)

    return queryResponse


# 8 Bytes Request Header
# 4 Bytes Element Header
# 5 Bytes Variable Header
def unmarshal(bytesStr):
    requestHeader = bytesStr[:9]
    (
        byteOrdering,
        serviceType,
        messageType,
        errorCode,
        on_off,
        noOfElement,
    ) = decodeRequestHeader(requestHeader)

    elementsByte = bytesStr[9:]
    print("ON OFFF euqal to: ", on_off)

    if on_off == 0:
        if errorCode != 0 and messageType == MessageType.REPLY:
            queryResponse = Response()
            queryResponse = decodeError(queryResponse, elementsByte, byteOrdering)
            return queryResponse, serviceType, errorCode

        if messageType == MessageType.REQUEST:
            queryRequest = []
            if serviceType == ServiceType.QUERY_FLIGHTID:
                queryRequest = [QueryFlightIdRequest() for i in range(noOfElement)]
            elif serviceType == ServiceType.QUERY_DEPARTURETIME:
                queryRequest = [QueryDepartureTimeRequest() for i in range(noOfElement)]
            elif serviceType == ServiceType.RESERVATION:
                queryRequest = [ReservationRequest() for i in range(noOfElement)]
            elif serviceType == ServiceType.MONITOR:
                queryRequest = [MonitorRequest() for i in range(noOfElement)]
            elif serviceType == ServiceType.CHECK_RESERVATION:
                queryRequest = [CheckReservationRequest() for i in range(noOfElement)]
            elif serviceType == ServiceType.CANCELLATION:
                queryRequest = [CancellationRequest() for i in range(noOfElement)]

            queryRequest = decodeQuery(
                queryRequest,
                elementsByte,
                byteOrdering,
                noOfElement,
                serviceType,
                messageType,
            )

            return queryRequest, serviceType, errorCode
        elif messageType == MessageType.REPLY:
            queryResponse = Response()
            if serviceType == ServiceType.QUERY_FLIGHTID:
                queryResponse.value = [QueryFlightIdResponse() for i in range(noOfElement)]
            elif serviceType == ServiceType.QUERY_DEPARTURETIME:
                queryResponse.value = [
                    QueryDepartureTimeResponse() for i in range(noOfElement)
                ]
            elif serviceType == ServiceType.RESERVATION:
                queryResponse.value = [ReservationResponse() for i in range(noOfElement)]
            elif serviceType == ServiceType.MONITOR:
                queryResponse.value = [MonitorResponse() for i in range(noOfElement)]
            elif serviceType == ServiceType.CHECK_RESERVATION:
                queryResponse.value = [
                    CheckReservationRequest() for i in range(noOfElement)
                ]
            elif serviceType == ServiceType.CANCELLATION:
                queryResponse.value = [CancellationResponse() for i in range(noOfElement)]

            queryResponse.value = decodeQuery(
                queryResponse.value,
                elementsByte,
                byteOrdering,
                noOfElement,
                serviceType,
                messageType,
            )

            return queryResponse, serviceType, errorCode
    elif on_off == 1:
        return "drop"


def marshal(r, serviceType, messageType, errorCode):
    length = 1
    resultSize = 0
    resultBytes = bytearray()

    if errorCode != 0 and messageType == MessageType.REPLY:
        errorBytes, errorSize = toBytes(r.error)
        errorBytes, errorSize = addVariableHeader(
            DataType.STRING_TYPE, errorSize, errorBytes, errorSize
        )
        errorBytes, errorSize = addElementHeader(errorSize, errorBytes, errorSize)

        resultSize += errorSize
        resultBytes.extend(errorBytes)
        bytes, size = addRequestHeader(
            serviceType, messageType, errorCode, length, resultBytes, resultSize
        )
        return bytes, size

    if messageType == MessageType.REQUEST:
        tempSize = 0
        tempBytes = bytearray()

        dataFields = r
        for field in fields(dataFields):
            fieldBytes, fieldSize = toBytes(getattr(dataFields, field.name))
            fieldBytes, fieldSize = addVariableHeader(
                getDataType(getattr(dataFields, field.name)),
                fieldSize,
                fieldBytes,
                fieldSize,
            )
            tempBytes.extend(fieldBytes)
            tempSize += fieldSize
        tempBytes, tempSize = addElementHeader(tempSize, tempBytes, tempSize)

        resultSize += tempSize
        resultBytes.extend(tempBytes)

    elif messageType == MessageType.REPLY:
        length = len(r.value)

        for dataFields in r.value:
            tempSize = 0
            tempBytes = bytearray()

            for field in fields(dataFields):
                fieldBytes, fieldSize = toBytes(getattr(dataFields, field.name))
                fieldBytes, fieldSize = addVariableHeader(
                    getDataType(getattr(dataFields, field.name)),
                    fieldSize,
                    fieldBytes,
                    fieldSize,
                )
                tempBytes.extend(fieldBytes)
                tempSize += fieldSize
            tempBytes, tempSize = addElementHeader(tempSize, tempBytes, tempSize)

            resultSize += tempSize
            resultBytes.extend(tempBytes)

    bytes, size = addRequestHeader(
        serviceType, messageType, errorCode, length, resultBytes, resultSize
    )
    return bytes, size
