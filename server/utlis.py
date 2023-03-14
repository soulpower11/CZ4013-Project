import struct
import time
from dataclasses import dataclass, fields
import string
import sys
import re
from consts import (
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


# Get the endianness of the system
def get_endianness():
    if sys.byteorder == "little":
        return ByteOrdering.LITTLE_ENDIAN
    else:
        return ByteOrdering.BIG_ENDIAN


# Functions to convert a variable type into byte array


def int_to_bytes(num):
    size = struct.calcsize("i")
    bytes_ = struct.pack("i", num)
    return bytes_, size


def int_to_byte(num):
    return num.to_bytes(1, byteorder="little")


def float_to_bytes(num):
    size = struct.calcsize("f")
    bytes_ = struct.pack("f", num)
    return bytes_, size


def string_to_bytes(string):
    bytes_ = string.encode("ascii")
    size = len(bytes_)
    return bytes_, size


def time_to_bytes(struct_time):
    size = struct.calcsize("Q")
    bytes_ = struct.pack("Q", int(time.mktime(struct_time)))
    return bytes_, size


# Takes in a variable and convert it into bytes
def to_bytes(variable):
    if type(variable) == int:
        return int_to_bytes(variable)
    elif type(variable) == float:
        return float_to_bytes(variable)
    elif type(variable) == str:
        return string_to_bytes(variable)
    elif type(variable) == string:
        return string_to_bytes(variable)
    elif type(variable) == time.struct_time:
        return time_to_bytes(variable)


# Functions to convert bytes back to its respective variable type


def bytes_to_int(bytes_, byte_order):
    return int.from_bytes(bytes_, byteorder=byte_order, signed=False)


def bytes_to_float(bytes_, byte_order):
    if byte_order == ByteOrdering.BIG_ENDIAN:
        return struct.unpack(">f", bytes_)[0]
    else:
        return struct.unpack("<f", bytes_)[0]


def bytes_to_string(bytes_):
    string = bytes_.decode("ascii")
    return string


def bytes_to_time(bytes_, byte_order):
    integer = int.from_bytes(bytes_, byteorder=byte_order, signed=False)
    t = time.localtime(integer)
    return t


# Takes in a byte array and convert it into variable
def to_variable(bytes_, data_type, byte_order):
    if data_type == DataType.INT_TYPE:
        return bytes_to_int(bytes_, byte_order)
    elif data_type == DataType.FLOAT_TYPE:
        return bytes_to_float(bytes_, byte_order)
    elif data_type == DataType.STRING_TYPE:
        return bytes_to_string(bytes_)
    elif data_type == DataType.TIME_TYPE:
        return bytes_to_time(bytes_, byte_order)


# Function to convert the byte ordering byte


def byte_ordering_to_byte(num):
    return num.to_bytes(1, byteorder="big")


def byte_ordering_from_byte(byte):
    return int.from_bytes(byte, byteorder="big", signed=False)


# Get the data type const of the variable
def get_data_type(variable):
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


# Add Request ID Bytes
# Contains a total of 23 Bytes
# IP 15 Bytes
# Time 8 Bytes
def add_request_id(ip, time, bytes_, size):
    result_bytes = bytearray(23 + size)

    ip_bytes, ip_size = to_bytes(ip)
    time_bytes, time_size = to_bytes(time)

    result_bytes[0:ip_size] = ip_bytes
    if ip_size != 15:
        padding = bytearray(15 - ip_size)
        result_bytes[ip_size:15] = padding

    result_bytes[15 : 15 + time_size] = time_bytes
    result_bytes[23 : 23 + size] = bytes_[:size]

    return result_bytes, 23 + size


# Add the Request Header Bytes
# Contains a total of 9 Bytes
# Service Type 1 Byte
# Message Type 1 Byte
# Byte Ordering 1 Byte
# Error Code 1 Byte
# Packet Loss 1 Byte
# No. of element 4 Bytes
def add_request_header(
    service_type, message_type, error_code, packet_loss, no_of_element, bytes_, size
):
    result_bytes = bytearray(9 + size)

    service_bytes = int_to_byte(service_type)
    message_bytes = int_to_byte(message_type)
    byte_ordering_bytes = int_to_byte(get_endianness())
    error_code_bytes = int_to_byte(error_code)
    time_out_bytes = int_to_byte(packet_loss)
    no_of_element_bytes, no_of_element_size = to_bytes(no_of_element)

    result_bytes[0:1] = service_bytes
    result_bytes[1:2] = message_bytes
    result_bytes[2:3] = byte_ordering_bytes
    result_bytes[3:4] = error_code_bytes
    result_bytes[4:5] = time_out_bytes
    result_bytes[5 : 5 + no_of_element_size] = no_of_element_bytes
    result_bytes[9 : 9 + size] = bytes_[:size]

    return result_bytes, 9 + size


# Add the Element Header Bytes
# Contain a total of 4 Bytes
# Length of Element 4 Bytes
def add_element_header(length, bytes_, size):
    result_bytes = bytearray(4 + size)

    length_bytes, length_size = to_bytes(length)
    result_bytes[0 : 0 + length_size] = length_bytes
    result_bytes[4 : 4 + size] = bytes_[:size]

    return result_bytes, 4 + size


# Data Type 1 Byte
# Length of variable 4 Byte
def add_variable_header(data_type, length, bytes_, size):
    result_bytes = bytearray(5 + size)

    data_type_bytes = int_to_byte(data_type)
    length_bytes, length_size = to_bytes(length)

    result_bytes[0:1] = data_type_bytes
    result_bytes[1 : 1 + length_size] = length_bytes
    result_bytes[5 : 5 + size] = bytes_[:size]

    return result_bytes, 5 + size


# Set the variable to the respective field
def set_field(data_class, index, value, service_type, message_type):
    if (
        service_type == ServiceType.QUERY_FLIGHT_ID
        and message_type == MessageType.REQUEST
    ):
        if index == 0:
            data_class.source = value
        elif index == 1:
            data_class.destination = value
    elif (
        service_type == ServiceType.QUERY_FLIGHT_ID
        and message_type == MessageType.REPLY
    ):
        if index == 0:
            data_class.flightId = value
    elif (
        service_type == ServiceType.QUERY_DEPARTURE_TIME
        and message_type == MessageType.REQUEST
    ):
        if index == 0:
            data_class.flightId = value
    elif (
        service_type == ServiceType.QUERY_DEPARTURE_TIME
        and message_type == MessageType.REPLY
    ):
        if index == 0:
            data_class.departureTime = value
        elif index == 1:
            data_class.airFare = value
        elif index == 2:
            data_class.seatAvailability = value
    elif (
        service_type == ServiceType.RESERVATION and message_type == MessageType.REQUEST
    ):
        if index == 0:
            data_class.flightId = value
        elif index == 1:
            data_class.noOfSeats = value
    elif service_type == ServiceType.RESERVATION and message_type == MessageType.REPLY:
        if index == 0:
            data_class.msg = value
    elif service_type == ServiceType.MONITOR and message_type == MessageType.REQUEST:
        if index == 0:
            data_class.flightId = value
        elif index == 1:
            data_class.monitorInterval = value
    elif service_type == ServiceType.MONITOR and message_type == MessageType.REPLY:
        if index == 0:
            data_class.msg = value
    elif (
        service_type == ServiceType.CHECK_RESERVATION
        and message_type == MessageType.REQUEST
    ):
        if index == 0:
            data_class.flightId = value
    elif (
        service_type == ServiceType.CHECK_RESERVATION
        and message_type == MessageType.REPLY
    ):
        if index == 0:
            data_class.seatsReserved = value
    elif (
        service_type == ServiceType.CANCELLATION and message_type == MessageType.REQUEST
    ):
        if index == 0:
            data_class.flightId = value
    elif service_type == ServiceType.CANCELLATION and message_type == MessageType.REPLY:
        if index == 0:
            data_class.msg = value

    return data_class


# Decode the IP address from the Request ID
def decode_ip_from_request_id(request_id):
    ip = bytes_to_string(request_id[0:15])

    return re.sub(r"[^.\d]+", "", ip)


# DecodeRequestHeader Decode the Request Header Bytes
def decode_request_header(request_header):
    byte_ordering = (
        "big"
        if byte_ordering_from_byte(request_header[2:3]) == ByteOrdering.BIG_ENDIAN
        else "little"
    )
    service_type = bytes_to_int(request_header[0:1], byte_ordering)
    message_type = bytes_to_int(request_header[1:2], byte_ordering)
    error_code = bytes_to_int(request_header[3:4], byte_ordering)
    packet_loss = bytes_to_int(request_header[4:5], byte_ordering)
    no_of_element = bytes_to_int(request_header[5:], byte_ordering)

    return (
        byte_ordering,
        service_type,
        message_type,
        error_code,
        packet_loss,
        no_of_element,
    )


# DecodeElementHeader Decode the Element Header Bytes
def decode_element_header(elements_byte, byte_ordering):
    length_of_element = bytes_to_int(elements_byte[:4], byte_ordering)
    variables_byte = elements_byte[4 : 4 + length_of_element]

    return length_of_element, variables_byte


# DecodeVariableHeader Decode the Variable Header Bytes
def decode_variable_header(variable_header, byte_ordering):
    data_type = bytes_to_int(variable_header[0:1], byte_ordering)
    length_of_variable = bytes_to_int(variable_header[1:], byte_ordering)

    return data_type, length_of_variable


# DecodeQuery Decode the bytes into each struct fields
def decode_query(
    query, elements_byte, byte_ordering, no_of_element, service_type, message_type
):
    for i in range(no_of_element):
        length_of_element, variables_byte = decode_element_header(
            elements_byte, byte_ordering
        )
        elements_byte = elements_byte[4 + length_of_element :]

        index = 0
        while len(variables_byte) != 0:
            variable_header = variables_byte[:5]
            data_type, length_of_variable = decode_variable_header(
                variable_header, byte_ordering
            )

            variable_byte = variables_byte[5 : 5 + length_of_variable]
            query[i] = set_field(
                query[i],
                index,
                to_variable(variable_byte, data_type, byte_ordering),
                service_type,
                message_type,
            )

            variables_byte = variables_byte[5 + length_of_variable :]
            index += 1

    return query


# DecodeError Decode the error message from bytes
def decode_error(query_response, elements_byte, byte_ordering):
    length_of_element, variables_byte = decode_element_header(
        elements_byte, byte_ordering
    )
    elements_byte = elements_byte[4 + length_of_element :]

    variable_header = variables_byte[:5]
    data_type, length_of_variable = decode_variable_header(
        variable_header, byte_ordering
    )
    variable_byte = variables_byte[5 : 5 + length_of_variable]

    query_response.error = to_variable(variable_byte, data_type, byte_ordering)

    return query_response


# The unmarshal function to unmarshal the bytes into struct. Containing
# 9 Bytes Request Header
# 4 Bytes Element Header
# 5 Bytes Variable Header
def unmarshal(bytes_str):
    request_header = bytes_str[:9]
    (
        byte_ordering,
        service_type,
        message_type,
        error_code,
        packet_loss,
        no_of_element,
    ) = decode_request_header(request_header)

    elements_byte = bytes_str[9:]

    if error_code != 0 and message_type == MessageType.REPLY:
        query_response = Response()
        query_response = decode_error(query_response, elements_byte, byte_ordering)
        return query_response, service_type, error_code, packet_loss

    if message_type == MessageType.REQUEST:
        query_request = []
        if service_type == ServiceType.QUERY_FLIGHT_ID:
            query_request = [QueryFlightIdRequest() for i in range(no_of_element)]
        elif service_type == ServiceType.QUERY_DEPARTURE_TIME:
            query_request = [QueryDepartureTimeRequest() for i in range(no_of_element)]
        elif service_type == ServiceType.RESERVATION:
            query_request = [ReservationRequest() for i in range(no_of_element)]
        elif service_type == ServiceType.MONITOR:
            query_request = [MonitorRequest() for i in range(no_of_element)]
        elif service_type == ServiceType.CHECK_RESERVATION:
            query_request = [CheckReservationRequest() for i in range(no_of_element)]
        elif service_type == ServiceType.CANCELLATION:
            query_request = [CancellationRequest() for i in range(no_of_element)]

        query_request = decode_query(
            query_request,
            elements_byte,
            byte_ordering,
            no_of_element,
            service_type,
            message_type,
        )

        return query_request, service_type, error_code, packet_loss
    elif message_type == MessageType.REPLY:
        query_response = Response()
        if service_type == ServiceType.QUERY_FLIGHT_ID:
            query_response.value = [
                QueryFlightIdResponse() for i in range(no_of_element)
            ]
        elif service_type == ServiceType.QUERY_DEPARTURE_TIME:
            query_response.value = [
                QueryDepartureTimeResponse() for i in range(no_of_element)
            ]
        elif service_type == ServiceType.RESERVATION:
            query_response.value = [ReservationResponse() for i in range(no_of_element)]
        elif service_type == ServiceType.MONITOR:
            query_response.value = [MonitorResponse() for i in range(no_of_element)]
        elif service_type == ServiceType.CHECK_RESERVATION:
            query_response.value = [
                CheckReservationResponse() for i in range(no_of_element)
            ]
        elif service_type == ServiceType.CANCELLATION:
            query_response.value = [
                CancellationResponse() for i in range(no_of_element)
            ]

        query_response.value = decode_query(
            query_response.value,
            elements_byte,
            byte_ordering,
            no_of_element,
            service_type,
            message_type,
        )

        return query_response, service_type, error_code, packet_loss


# Marshal The marshaling function
# Marshal the struct into bytes
def marshal(r, service_type, message_type, error_code, packet_loss):
    length = 1
    result_size = 0
    result_bytes = bytearray()

    if error_code != 0 and message_type == MessageType.REPLY:
        error_bytes, error_size = to_bytes(r.error)
        error_bytes, error_size = add_variable_header(
            DataType.STRING_TYPE, error_size, error_bytes, error_size
        )
        error_bytes, error_size = add_element_header(
            error_size, error_bytes, error_size
        )

        result_size += error_size
        result_bytes.extend(error_bytes)
        bytes, size = add_request_header(
            service_type,
            message_type,
            error_code,
            packet_loss,
            length,
            result_bytes,
            result_size,
        )
        return bytes, size

    if message_type == MessageType.REQUEST:
        temp_size = 0
        temp_bytes = bytearray()

        data_fields = r
        for field in fields(data_fields):
            field_bytes, field_size = to_bytes(getattr(data_fields, field.name))
            field_bytes, field_size = add_variable_header(
                get_data_type(getattr(data_fields, field.name)),
                field_size,
                field_bytes,
                field_size,
            )
            temp_bytes.extend(field_bytes)
            temp_size += field_size
        temp_bytes, temp_size = add_element_header(temp_size, temp_bytes, temp_size)

        result_size += temp_size
        result_bytes.extend(temp_bytes)

    elif message_type == MessageType.REPLY:
        length = len(r.value)

        for data_fields in r.value:
            temp_size = 0
            temp_bytes = bytearray()

            for field in fields(data_fields):
                field_bytes, field_size = to_bytes(getattr(data_fields, field.name))
                field_bytes, field_size = add_variable_header(
                    get_data_type(getattr(data_fields, field.name)),
                    field_size,
                    field_bytes,
                    field_size,
                )
                temp_bytes.extend(field_bytes)
                temp_size += field_size
            temp_bytes, temp_size = add_element_header(temp_size, temp_bytes, temp_size)

            result_size += temp_size
            result_bytes.extend(temp_bytes)

    bytes, size = add_request_header(
        service_type,
        message_type,
        error_code,
        packet_loss,
        length,
        result_bytes,
        result_size,
    )
    return bytes, size
