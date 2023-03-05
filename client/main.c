/*
    Simple udp client
*/
#include <stdio.h>
#include <winsock2.h>
#include "utils.h"
#include <time.h>

#pragma comment(lib, "ws2_32.lib") // Winsock Library

#define SERVER "127.0.0.1" // ip address of udp server
#define BUFLEN 512         // Max length of buffer
#define PORT 8080          // The port on which to listen for incoming data

int main(void)
{
    struct sockaddr_in si_other;
    int s, slen = sizeof(si_other);
    char buf[BUFLEN];
    char message[BUFLEN];
    WSADATA wsa;

    // Initialise winsock
    printf("\nInitialising Winsock...");
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        printf("Failed. Error Code : %d", WSAGetLastError());
        exit(EXIT_FAILURE);
    }
    printf("Initialised.\n");

    // create socket
    if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == SOCKET_ERROR)
    {
        printf("socket() failed with error code : %d", WSAGetLastError());
        exit(EXIT_FAILURE);
    }

    // setup address structure
    memset((char *)&si_other, 0, sizeof(si_other));
    si_other.sin_family = AF_INET;
    si_other.sin_port = htons(PORT);
    si_other.sin_addr.S_un.S_addr = inet_addr(SERVER);

    Request r1 = {QUERY_FLIGHTID, REQUEST, {.qfi = &(QueryFlightIdRequest){.source = "Malaysia", .destination = "Singapore"}}};
    unsigned char *bytes;
    int size;
    marshal(r1, &bytes, &size);

    // Get the local host name
    char hostName[256];
    if (gethostname(hostName, sizeof(hostName)) != 0)
    {
        printf("gethostname failed with error: %d\n", WSAGetLastError());
        return 1;
    }

    // Get the host information
    struct hostent *hostInfo;
    hostInfo = gethostbyname(hostName);
    if (hostInfo == NULL)
    {
        printf("gethostbyname failed with error: %d\n", WSAGetLastError());
        return 1;
    }

    // Print the IP address
    struct in_addr *ipAddress;
    ipAddress = (struct in_addr *)*hostInfo->h_addr_list;
    char *ip = inet_ntoa(*ipAddress);
    time_t curTime = time(0);

    addRequestID(ip, curTime, &bytes, &size);

    // addRequestHeader(QUERY_FLIGHTID, REQUEST, 1, &bytes, &size);
    printf("The size is %d\n", size);
    for (int i = 0; i < size; i++)
    {
        printf("%02x ", bytes[i]);
    }
    printf("\n");

    // send the message
    if (sendto(s, bytes, size, 0, (struct sockaddr *)&si_other, slen) == SOCKET_ERROR)
    {
        printf("sendto() failed with error code : %d", WSAGetLastError());
        exit(EXIT_FAILURE);
    }

    // receive a reply and print it
    // clear the buffer by filling null, it might have previously received data
    memset(buf, '\0', BUFLEN);
    // try to receive some data, this is a blocking call
    if (recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *)&si_other, &slen) == SOCKET_ERROR)
    {
        printf("recvfrom() failed with error code : %d", WSAGetLastError());
        exit(EXIT_FAILURE);
    }

    puts(buf);

    Request r2 = unmarshal(buf + 20);
    printf("The error is: %s\n", r2.value.qfir.error);
    // size_t len = r2.length;
    // for (int i = 0; i < len; i++)
    // {
    //     printf("The Flight ID is: %d\n", r2.value.qfir.flightIds[i]);
    // }

    free(bytes);

    // // start communication
    // while (1)
    // {
    //     printf("Enter message : ");
    //     gets(message);

    //     // send the message
    //     if (sendto(s, message, strlen(message), 0, (struct sockaddr *)&si_other, slen) == SOCKET_ERROR)
    //     {
    //         printf("sendto() failed with error code : %d", WSAGetLastError());
    //         exit(EXIT_FAILURE);
    //     }

    //     // receive a reply and print it
    //     // clear the buffer by filling null, it might have previously received data
    //     memset(buf, '\0', BUFLEN);
    //     // try to receive some data, this is a blocking call
    //     if (recvfrom(s, buf, BUFLEN, 0, (struct sockaddr *)&si_other, &slen) == SOCKET_ERROR)
    //     {
    //         printf("recvfrom() failed with error code : %d", WSAGetLastError());
    //         exit(EXIT_FAILURE);
    //     }

    //     puts(buf);
    // }

    closesocket(s);
    WSACleanup();

    return 0;
}