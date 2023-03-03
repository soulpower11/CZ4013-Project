#include <stdio.h>
#include <time.h>

typedef enum DataType
{
    INT_TYPE,
    FLOAT_TYPE,
    STRING_TYPE,
    TIME_TYPE,
} DataType;

typedef union DataValue
{
    int i;
    float f;
    char *s;
    time_t t;
} DataValue;

typedef struct DynamicDataType
{
    DataType type;
    DataValue value;
} DynamicDataType;

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

typedef enum RequestType
{
    QUERY_FLIGHTID,
} RequestType;

typedef union RequestValue
{
    struct QueryFlightIdRequest qfi;
} RequestValue;

typedef struct Request
{
    RequestType type;
    RequestValue value;
} Request;

void timeToBytes(time_t time, unsigned char **bytes, int *size)
{
    *size = sizeof(time_t);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, &time, *size);
}

void intToBytes(int num, unsigned char **bytes, int *size)
{
    *size = sizeof(int);
    *bytes = (unsigned char *)malloc(*size);
    memcpy(*bytes, &num, *size);
}

unsigned char intToByte2(int num)
{
    unsigned char byte;
    memcpy(&byte, &num, sizeof(unsigned char));
    return byte;
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

void marshall(Request r, unsigned char **bytes, int *size)
{
    switch (r.type)
    {
    case QUERY_FLIGHTID:
        unsigned char *sourceBytes;
        int sourceSize;
        unsigned char *destinationBytes;
        int destinationSize;

        stringToBytes(r.value.qfi.source, &sourceBytes, &sourceSize);
        stringToBytes(r.value.qfi.destination, &destinationBytes, &destinationSize);

        *size = sourceSize + destinationSize;
        *bytes = (unsigned char *)malloc(*size);

        memcpy(*bytes, sourceBytes, sourceSize);
        memcpy(*bytes + sourceSize, destinationBytes, destinationSize);
        break;
    default:
        break;
    }
}

// IP+Time
void addRequestID()
{
}

// Service Type 1 Byte
// No. of element 1 Byte
// Byte Ordering 1 Byte
void addRequestHeader()
{
}

// Length of Element 4 Byte
void addElementHeader()
{
}

// Data Type 1 Byte
// Length of variable 4 Byte
void addVariableHeader()
{
}

// void toBytes(DynamicDataType v, unsigned char **bytes, int *size)
// {
//     switch (v.type)
//     {
//     case INT_TYPE:
//         intToBytes(v.value.i, bytes, size);
//         // printf("Value: %d\n", v.value.i);
//         break;
//     case FLOAT_TYPE:
//         // printf("Value: %f\n", v.value.f);
//         break;
//     case STRING_TYPE:
//         // printf("Value: %s\n", v.value.s);
//         break;
//     case TIME_TYPE:
//         // char time_string[7]; // HH:MM\0
//         // strftime(time_string, sizeof(time_string), "%H:%M", localtime(&v.value.t));
//         // printf("Current time: %s\n", time_string);
//         break;
//     default:
//         // printf("Unknown type\n");
//         break;
//     }
// }