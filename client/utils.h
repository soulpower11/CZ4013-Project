#include <stdio.h>
#include <time.h>

typedef enum DataType
{
    INT_TYPE,
    FLOAT_TYPE,
    STRING_TYPE,
    TIME_TYPE,
} DataType;

typedef enum ServiceType
{
    QUERY_FLIGHTID,
    QUERY_DEPARTURETIME,
    RESERVATION,
    MONITOR,
    CHECK_ARRIVALTIME,
    CANCALLATION,
} ServiceType;

typedef enum MessageType
{
    REQUEST,
    REPLY,
} MessageType;

typedef enum ByteOrdering
{
    BIG_ENDIAN,
    LITTLE_ENDIAN,
} ByteOrdering;

typedef struct QueryFlightIdRequest
{
    char *source;
    char *destination;
} QueryFlightIdRequest;

typedef struct QueryFlightIdResponse
{
    int *flightId;
    char *error;
} QueryFlightIdResponse;

typedef struct QueryDepartureTimeRequest
{
    int flightId;
} QueryDepartureTimeRequest;

typedef struct QueryDepartureTimeResponse
{
    time_t departureTime;
    float airFare;
    int seatAvailability;
    char *error;
} QueryDepartureTimeResponse;

typedef struct ReservationRequest
{
    int flightId;
    int noOfSeats;
} ReservationRequest;

typedef struct ReservationResponse
{
    char *msg;
    char *error;
} ReservationResponse;

typedef struct MonitorRequest
{
    int flightId;
    int monitorInterval;
} MonitorRequest;

typedef struct MonitorResponse
{
    char *msg;
    char *error;
} MonitorResponse;

typedef struct CheckArrivalTimeRequest
{
    int flightId;
} CheckArrivalTimeRequest;

typedef struct CheckArrivalTimeResponse
{
    time_t arrivalTime;
    char *error;
} CheckArrivalTimeResponse;

typedef struct CancellationRequest
{
    int flightId;
} CancellationRequest;

typedef struct CancellationResponse
{
    char *msg;
    char *error;
} CancellationResponse;

typedef union RequestValue
{
    struct QueryFlightIdRequest qfi;
    struct QueryDepartureTimeRequest qdt;
    struct ReservationRequest r;
    struct MonitorRequest m;
    struct CheckArrivalTimeRequest cat;
    struct CancellationRequest c;
} RequestValue;

typedef struct Request
{
    ServiceType type;
    RequestValue value;
} Request;

void intToBytes(int num, unsigned char **bytes, int *size)
{
    *size = sizeof(int);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, &num, *size);
}

void intToByte(int num, unsigned char **bytes)
{
    *bytes = (unsigned char *)malloc(1);
    memcpy(*bytes, &num, 1);
}

void floatToBytes(float num, unsigned char **bytes, int *size)
{
    *size = sizeof(float);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, &num, *size);
}

void stringToBytes(char *str, unsigned char **bytes, int *size)
{
    *size = strlen(str);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, str, *size);
}

void timeToBytes(time_t time, unsigned char **bytes, int *size)
{
    *size = sizeof(time_t);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, &time, *size);
}

int getEndianness()
{
    int num = 1;
    if (*(char *)&num == 1)
    {
        return LITTLE_ENDIAN;
    }
    return BIG_ENDIAN;
}

// IP+Time
void addRequestID(char *ip, unsigned char **bytes, int *size)
{
}

// Service Type 1 Byte
// Message Type 1 Byte
// Byte Ordering 1 Byte
// No. of element 4 Byte
void addRequestHeader(int serviceType, int messageType, int noOfElement, unsigned char **bytes, int *size)
{
    unsigned char *resultBytes;
    unsigned char *serviceBytes;
    unsigned char *messageBytes;
    unsigned char *byteOrderingBytes;
    unsigned char *noOfElementBytes;
    int noOfElementSize;

    resultBytes = (unsigned char *)malloc(7 + *size);

    intToByte(serviceType, &serviceBytes);
    intToByte(messageType, &messageBytes);
    intToByte(getEndianness(), &byteOrderingBytes);
    intToBytes(noOfElement, &noOfElementBytes, &noOfElementSize);

    memcpy(resultBytes, serviceBytes, 1);
    memcpy(resultBytes + 1, messageBytes, 1);
    memcpy(resultBytes + 2, byteOrderingBytes, 1);
    memcpy(resultBytes + 3, noOfElementBytes, noOfElementSize);
    memcpy(resultBytes + 7, *bytes, *size);

    *bytes = resultBytes;
    *size += 7;
}

// Length of Element 4 Byte
void addElementHeader(int length, unsigned char **bytes, int *size)
{
    unsigned char *resultBytes;
    unsigned char *lengtBytes;
    int lengthSize;

    resultBytes = (unsigned char *)malloc(4 + *size);

    intToBytes(length, &lengtBytes, &lengthSize);

    memcpy(resultBytes, lengtBytes, lengthSize);
    memcpy(resultBytes + 4, *bytes, *size);

    *bytes = resultBytes;
    *size += 4;
}

// Data Type 1 Byte
// Length of variable 4 Byte
void addVariableHeader(int dataType, int length, unsigned char **bytes, int *size)
{
    unsigned char *resultBytes;
    unsigned char *dataTypeBytes;
    unsigned char *lengthBytes;
    int lengthSize;

    resultBytes = (unsigned char *)malloc(5 + *size);

    intToByte(dataType, &dataTypeBytes);
    intToBytes(length, &lengthBytes, &lengthSize);

    memcpy(resultBytes, dataTypeBytes, 1);
    memcpy(resultBytes + 1, lengthBytes, lengthSize);
    memcpy(resultBytes + 5, *bytes, *size);

    *bytes = resultBytes;
    *size += 5;
}

void marshall(Request r, unsigned char **bytes, int *size)
{
    switch (r.type)
    {
    case QUERY_FLIGHTID:
        unsigned char *resultBytes;
        int resultSize;
        unsigned char *sourceBytes;
        int sourceSize;
        unsigned char *destinationBytes;
        int destinationSize;

        stringToBytes(r.value.qfi.source, &sourceBytes, &sourceSize);
        addVariableHeader(STRING_TYPE, sourceSize, &sourceBytes, &sourceSize);

        stringToBytes(r.value.qfi.destination, &destinationBytes, &destinationSize);
        addVariableHeader(STRING_TYPE, destinationSize, &destinationBytes, &destinationSize);

        resultSize = sourceSize + destinationSize;
        resultBytes = (unsigned char *)malloc(resultSize);

        memcpy(resultBytes, sourceBytes, sourceSize);
        memcpy(resultBytes + sourceSize, destinationBytes, destinationSize);
        addElementHeader(resultSize, &resultBytes, &resultSize);

        *size = resultSize;
        *bytes = (unsigned char *)malloc(*size);

        memcpy(*bytes, resultBytes, resultSize);
        addRequestHeader(QUERY_FLIGHTID, REQUEST, 2, bytes, size);

        free(sourceBytes);
        free(destinationBytes);
        break;
    default:
        break;
    }
}