#include <stdio.h>
#include <time.h>
#include "serviceType.h"

unsigned char *slice(unsigned char *arr, int start, int end)
{
    int length = end - start;
    unsigned char *result = malloc(length * sizeof(unsigned char));
    for (int i = 0; i < length; i++)
    {
        result[i] = arr[start + i];
    }
    return result;
}

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

int bytesToInt(unsigned char *bytes, int byteOrder)
{
    int numBytes = sizeof(int);
    int value = 0;

    if (byteOrder == LITTLE_ENDIAN)
    {
        for (int i = numBytes - 1; i >= 0; i--)
        {
            value = (value << 8) + bytes[i];
        }
    }
    else
    {
        for (int i = 0; i < numBytes; i++)
        {
            value = (value << 8) + bytes[i];
        }
    }

    return value;
}

int byteToInt(unsigned char byte)
{
    return (int)byte;
}

float bytesToFloat(unsigned char *bytes, int byteOrder)
{
    int numBytes = sizeof(float);
    float value = 0.0f;

    if (byteOrder == LITTLE_ENDIAN)
    {
        for (int i = numBytes - 1; i >= 0; i--)
        {
            ((unsigned char *)&value)[i] = bytes[i];
        }
    }
    else
    {
        for (int i = 0; i < numBytes; i++)
        {
            ((unsigned char *)&value)[i] = bytes[i];
        }
    }

    return value;
}

char *bytesToString(unsigned char *bytes, int numBytes)
{
    char *string = (unsigned char *)malloc(numBytes);

    for (int i = 0; i < numBytes; i++)
    {
        string[i] = (char)bytes[i];
    }

    string[numBytes] = '\0';

    return string;
}

time_t bytesToTime(unsigned char *bytes, int byteOrder)
{
    int numBytes = sizeof(time_t);
    time_t value = 0;

    if (byteOrder == LITTLE_ENDIAN)
    {
        for (int i = numBytes - 1; i >= 0; i--)
        {
            ((unsigned char *)&value)[i] = bytes[i];
        }
    }
    else
    {
        for (int i = 0; i < numBytes; i++)
        {
            ((unsigned char *)&value)[i] = bytes[i];
        }
    }

    return value;
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

unsigned char byteOrderingToByte(int num)
{
    unsigned char byte = (num >> 0) & 0xFF;
    return byte;
}

// IP+Time 19 Bytes
void addRequestID(char *ip, time_t time, unsigned char **bytes, int *size)
{
    unsigned char *resultBytes;
    unsigned char *ipBytes;
    unsigned char *timeBytes;
    int ipSize;
    int timeSize;

    stringToBytes(ip, &ipBytes, &ipSize);
    timeToBytes(time, &timeBytes, &timeSize);

    resultBytes = (unsigned char *)malloc(20 + *size);

    memcpy(resultBytes, ipBytes, ipSize);
    memcpy(resultBytes + 12, timeBytes, timeSize);
    memcpy(resultBytes + 12 + timeSize, *bytes, *size);

    *bytes = resultBytes;
    *size += 20;
}

// Service Type 1 Byte
// Message Type 1 Byte
// Byte Ordering 1 Byte
// Error Code 1 Byte
// No. of element 4 Byte
void addRequestHeader(int serviceType, int messageType, int errorCode, int noOfElement, unsigned char **bytes, int *size)
{
    unsigned char *resultBytes;
    unsigned char *serviceBytes;
    unsigned char *messageBytes;
    unsigned char byteOrderingBytes;
    unsigned char *errorCodeByte;
    unsigned char *noOfElementBytes;
    int noOfElementSize;

    resultBytes = (unsigned char *)malloc(8 + *size);

    intToByte(serviceType, &serviceBytes);
    intToByte(messageType, &messageBytes);
    byteOrderingBytes = byteOrderingToByte(getEndianness());
    intToByte(errorCode, &errorCodeByte);
    intToBytes(noOfElement, &noOfElementBytes, &noOfElementSize);

    memcpy(resultBytes, serviceBytes, 1);
    memcpy(resultBytes + 1, messageBytes, 1);
    memcpy(resultBytes + 2, &byteOrderingBytes, 1);
    memcpy(resultBytes + 3, errorCodeByte, 1);
    memcpy(resultBytes + 4, noOfElementBytes, noOfElementSize);
    memcpy(resultBytes + 8, *bytes, *size);

    *bytes = resultBytes;
    *size += 8;
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

Message unmarshal(unsigned char *bytes)
{
    unsigned char requestHeader[8];
    memcpy(requestHeader, bytes, 8);

    int serviceType = byteToInt(requestHeader[0]);
    int messageType = byteToInt(requestHeader[1]);
    int byteOrdering = byteToInt(requestHeader[2]);
    int errorCode = byteToInt(requestHeader[3]);
    int noOfElement = bytesToInt(slice(requestHeader, 4, 8), byteOrdering);

    unsigned char *elementsByte = bytes + 8;

    if (serviceType == QUERY_FLIGHTID && messageType == REQUEST)
    {
        QueryFlightIdRequest *queryRequest;
        queryRequest = (QueryFlightIdRequest *)malloc(noOfElement);
        for (int i = 0; i < noOfElement; i++)
        {
            int lengthOfElement = bytesToInt(slice(elementsByte, 0, 4), byteOrdering);
            unsigned char *variablesByte = elementsByte + 4;
            elementsByte += 4 + lengthOfElement;

            int index = 0;
            while (lengthOfElement != 0)
            {
                unsigned char variableHeader[5];
                memcpy(variableHeader, variablesByte, 5);

                int dataType = byteToInt(variableHeader[0]);
                int lengthOfVariable = bytesToInt(slice(variableHeader, 1, 5), byteOrdering);

                unsigned char *variableByte;
                variableByte = (unsigned char *)malloc(lengthOfVariable);
                memcpy(variableByte, variablesByte + 5, lengthOfVariable);

                if (index == 0)
                {
                    queryRequest[i].source = bytesToString(variableByte, lengthOfVariable);
                }
                else if (index == 1)
                {
                    queryRequest[i].destination = bytesToString(variableByte, lengthOfVariable);
                }

                variablesByte += 5 + lengthOfVariable;
                lengthOfElement -= (5 + lengthOfVariable);
                index++;
            }
        }

        return (Message){serviceType, messageType, .value.qfi = queryRequest, noOfElement};
    }
    else if (serviceType == QUERY_FLIGHTID && messageType == REPLY)
    {
        QueryFlightIdResponse *queryResponse;
        queryResponse = (QueryFlightIdResponse *)malloc(noOfElement);
        if (errorCode == 0)
        {
            for (int i = 0; i < noOfElement; i++)
            {
                int lengthOfElement = bytesToInt(slice(elementsByte, 0, 4), byteOrdering);
                unsigned char *variablesByte = elementsByte + 4;
                elementsByte += 4 + lengthOfElement;

                int index = 0;
                while (lengthOfElement != 0)
                {
                    unsigned char variableHeader[5];
                    memcpy(variableHeader, variablesByte, 5);

                    int dataType = byteToInt(variableHeader[0]);
                    int lengthOfVariable = bytesToInt(slice(variableHeader, 1, 5), byteOrdering);

                    unsigned char *variableByte;
                    variableByte = (unsigned char *)malloc(lengthOfVariable);
                    memcpy(variableByte, variablesByte + 5, lengthOfVariable);

                    if (index == 0)
                    {
                        queryResponse[i].flightId = bytesToInt(variableByte, byteOrdering);
                    }

                    variablesByte += 5 + lengthOfVariable;
                    lengthOfElement -= (5 + lengthOfVariable);
                    index++;
                }
            }
        }
        else
        {
            int lengthOfElement = bytesToInt(slice(elementsByte, 0, 4), byteOrdering);
            unsigned char *variablesByte = elementsByte + 4;
            elementsByte += 4 + lengthOfElement;

            unsigned char variableHeader[5];
            memcpy(variableHeader, variablesByte, 5);

            int dataType = byteToInt(variableHeader[0]);
            int lengthOfVariable = bytesToInt(slice(variableHeader, 1, 5), byteOrdering);

            unsigned char *variableByte;
            variableByte = (unsigned char *)malloc(lengthOfVariable);
            memcpy(variableByte, variablesByte + 5, lengthOfVariable);

            char *error = bytesToString(variableByte, lengthOfVariable);
            Response r = {.error = error};
            return (Message){serviceType, messageType, .value.res = r, 1};
        }
        Response r = {.value = queryResponse};
        return (Message){serviceType, messageType, .value.res = r, noOfElement};
    }
}

void marshal(Message r, unsigned char **bytes, int *size)
{

    if (r.sType == QUERY_FLIGHTID && r.mType == REQUEST)
    {
        unsigned char *resultBytes;
        int resultSize;
        unsigned char *sourceBytes;
        int sourceSize;
        unsigned char *destinationBytes;
        int destinationSize;

        stringToBytes(r.value.qfi[0].source, &sourceBytes, &sourceSize);
        addVariableHeader(STRING_TYPE, sourceSize, &sourceBytes, &sourceSize);

        stringToBytes(r.value.qfi[0].destination, &destinationBytes, &destinationSize);
        addVariableHeader(STRING_TYPE, destinationSize, &destinationBytes, &destinationSize);

        resultSize = sourceSize + destinationSize;
        resultBytes = (unsigned char *)malloc(resultSize);

        memcpy(resultBytes, sourceBytes, sourceSize);
        memcpy(resultBytes + sourceSize, destinationBytes, destinationSize);
        addElementHeader(resultSize, &resultBytes, &resultSize);

        *size = resultSize;
        *bytes = (unsigned char *)malloc(*size);

        memcpy(*bytes, resultBytes, resultSize);
        addRequestHeader(QUERY_FLIGHTID, REQUEST, 0, 1, bytes, size);

        free(sourceBytes);
        free(destinationBytes);
    }
    else if (r.sType == QUERY_FLIGHTID && r.mType == REPLY)
    {
        unsigned char *resultBytes;
        int resultSize;
        unsigned char *sourceBytes;
        int sourceSize;
        unsigned char *destinationBytes;
        int destinationSize;

        stringToBytes(r.value.qfi[0].source, &sourceBytes, &sourceSize);
        addVariableHeader(STRING_TYPE, sourceSize, &sourceBytes, &sourceSize);

        stringToBytes(r.value.qfi[0].destination, &destinationBytes, &destinationSize);
        addVariableHeader(STRING_TYPE, destinationSize, &destinationBytes, &destinationSize);

        resultSize = sourceSize + destinationSize;
        resultBytes = (unsigned char *)malloc(resultSize);

        memcpy(resultBytes, sourceBytes, sourceSize);
        memcpy(resultBytes + sourceSize, destinationBytes, destinationSize);
        addElementHeader(resultSize, &resultBytes, &resultSize);

        *size = resultSize;
        *bytes = (unsigned char *)malloc(*size);

        memcpy(*bytes, resultBytes, resultSize);
        addRequestHeader(QUERY_FLIGHTID, REQUEST, 0, 1, bytes, size);

        free(sourceBytes);
        free(destinationBytes);
    }
}