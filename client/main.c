/*
    Simple udp client
*/
#include <stdio.h>
#include <winsock2.h>
#include "utils.h"
#include <time.h>

#pragma comment(lib, "ws2_32.lib") // Winsock Library (-lws2_32)

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

    printf("----- Welcome to our airplane service -----\n");
    printf(" Please select your choice: \n 1) Look for available flight \n 2) Flight details \
            \n 3) Make seat reservation \n 4) Monitor flight \n 5) Check arrival time \n 6) Cancel seat reservation \n");
    int choice, Numseat, total_length, offset;
    char TimePeriod[256];
    char ReceivedFrom[256];
    char buffer[1024];
    char input[100];
    char input2[100];
    unsigned char *bytes;
    int size,  Flight_iden;
    printf("Choice: ");
    scanf("%d", &choice);
    getchar(); // consume the newline character left in the input stream

    switch(choice){
        case 1:
            printf("Please enter your source: ");
            fgets(input, sizeof(input), stdin);
            input[strcspn(input, "\n")] = '\0'; // remove the newline character

            printf("Please enter your destination: ");
            fgets(input2, sizeof(input2), stdin);
            input2[strcspn(input2, "\n")] = '\0'; // remove the newline character

            Request r1 = {QUERY_FLIGHTID, REQUEST, {.qfi = &(QueryFlightIdRequest){.source = input, .destination = input2}}};
            printf("What the user have entered: Choice: %d. To traval from %s to %s \n", choice, input , input2);
            marshal(r1, &bytes, &size);
            break;
        case 2:
            printf("Please enter flight identifier: ");
            scanf("%d", &Flight_iden);
            //Request r1 = {QUERY_FLIGHTID, REQUEST, {.qfi = &(QueryFlightIdRequest){.source = input, .destination = input2}}};
            break;
        case 3:
            printf("Please enter the flight identifier: ");
            scanf("%d", &Flight_iden);
            printf("How many seats you want to reserve?");
            scanf("%d", &Numseat);
            getchar(); // consume the newline character left in the input stream
        case 4:
            printf("Please enter the flight identifier: ");
            scanf("%d", &Flight_iden);
            printf("Please enter the time period: ");
            fgets(TimePeriod, 255, stdin);
        case 5:
            printf("Please enter the flight identifier: ");
            scanf("%d", &Flight_iden);
        case 6:
            printf("Please enter the flight identifier: ");
            scanf("%d", &Flight_iden);
            printf("How many seats you want to reserve?");
            scanf("%d", &Numseat);
            getchar(); // consume the newline character left in the input stream
        default:
            exit(0);
    }

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
    Request r2 = unmarshal(buf);

    if(choice == 1){
        printf("Available flight IDs: %d \n", sizeof(r2.value.qfir.flightIds));
        for(int i =0; i<=sizeof(r2.value.qfir.flightIds); i++){
            printf("FlightID: %d\n", r2.value.qfir.flightIds[i]);
        }
    }else if(choice == 2){
        printf("Flight details of %d: \nDeparting time: %d\nAirfare: %f\nNumber of seat: %d",Flight_iden);
    }else if(choice == 3){

    }

    //printf("The FlightID is: %d \n", r2.value.qfir.flightIds[0]);

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