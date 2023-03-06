import socket
import sys
import time
import utlis

ip = "127.0.0.1"
port = 8080

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (ip, port)
s.bind(server_address)
print("Do Ctrl+c to exit the program !!")

while True:
    print("####### Server is listening #######")
    data, address = s.recvfrom(4096)
    requestId = data[:20]
    print(requestId)
    request = utlis.unmarshal(data[20:])
    print(
        "\n\n 2. Server received: ", request[0].source, request[0].destination, "\n\n"
    )

    # requestMarshal, _ = utlis.marshal(
    #     utlis.QueryFlightIdRequest("Malaysia", "Singapore"),
    #     utlis.ServiceType.QUERY_FLIGHTID,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    # r1 = utlis.unmarshal(requestMarshal)
    # print("Source:", r1[0].source, "Destination:", r1[0].destination)

    # replyMarshal, _ = utlis.marshal(
    #     utlis.Response(
    #         [
    #             utlis.QueryFlightIdResponse(52),
    #             utlis.QueryFlightIdResponse(25),
    #             utlis.QueryFlightIdResponse(351),
    #         ]
    #     ),
    #     utlis.ServiceType.QUERY_FLIGHTID,
    #     utlis.MessageType.REPLY,
    #     0,
    # )
    # r2 = utlis.unmarshal(replyMarshal)
    # # print(r2.error)
    # for value in r2.value:
    #     print(
    #         "Flight ID:",
    #         value.flightId,
    #     )

    # requestMarshal, _ = utlis.marshal(
    #     utlis.QueryDepartureTimeRequest(555),
    #     utlis.ServiceType.QUERY_DEPARTURETIME,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    # r1 = utlis.unmarshal(requestMarshal)
    # print("Flight ID:", r1[0].flightId)

    # replyMarshal, _ = utlis.marshal(
    #     utlis.Response(
    #         [
    #             utlis.QueryDepartureTimeResponse(time.localtime(), 54.32, 50),
    #             utlis.QueryDepartureTimeResponse(time.localtime(), 99.99, 152),
    #             utlis.QueryDepartureTimeResponse(time.localtime(), 551.99, 21),
    #             utlis.QueryDepartureTimeResponse(time.localtime(), 987.52, 654),
    #         ]
    #     ),
    #     utlis.ServiceType.QUERY_DEPARTURETIME,
    #     utlis.MessageType.REPLY,
    #     0,
    # )
    # r2 = utlis.unmarshal(replyMarshal)
    # # print(r2.error)
    # for value in r2.value:
    #     print(
    #         "Time:",
    #         value.departureTime,
    #         "Air Fare:",
    #         value.airFare,
    #         "Seat Availability",
    #         value.seatAvailability,
    #     )

    # requestMarshal, _ = utlis.marshal(
    #     utlis.ReservationRequest(554, 2),
    #     utlis.ServiceType.RESERVATION,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    # r1 = utlis.unmarshal(requestMarshal)
    # print("Flight ID:", r1[0].flightId, "No. of Seats:", r1[0].noOfSeats)

    # replyMarshal, _ = utlis.marshal(
    #     utlis.Response(
    #         [
    #             utlis.ReservationResponse("Done!"),
    #         ]
    #     ),
    #     utlis.ServiceType.RESERVATION,
    #     utlis.MessageType.REPLY,
    #     0,
    # )
    # r2 = utlis.unmarshal(replyMarshal)
    # # print(r2.error)
    # for value in r2.value:
    #     print(
    #         "Msg:",
    #         value.msg,
    #     )

    # requestMarshal, _ = utlis.marshal(
    #     utlis.MonitorRequest(335, 6),
    #     utlis.ServiceType.MONITOR,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    # r1 = utlis.unmarshal(requestMarshal)
    # print("Flight ID:", r1[0].flightId, "Monitor Interval:", r1[0].monitorInterval)

    # replyMarshal, _ = utlis.marshal(
    #     utlis.Response(
    #         [
    #             utlis.MonitorResponse("Update!"),
    #         ]
    #     ),
    #     utlis.ServiceType.RESERVATION,
    #     utlis.MessageType.REPLY,
    #     0,
    # )
    # r2 = utlis.unmarshal(replyMarshal)
    # # print(r2.error)
    # for value in r2.value:
    #     print(
    #         "Msg:",
    #         value.msg,
    #     )

    # requestMarshal, _ = utlis.marshal(
    #     utlis.CheckArrivalTimeRequest(542),
    #     utlis.ServiceType.CHECK_ARRIVALTIME,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    # r1 = utlis.unmarshal(requestMarshal)
    # print("Flight ID:", r1[0].flightId)

    # replyMarshal, _ = utlis.marshal(
    #     utlis.Response(
    #         [
    #             utlis.CheckArrivalTimeResponse(time.localtime()),
    #         ]
    #     ),
    #     utlis.ServiceType.CHECK_ARRIVALTIME,
    #     utlis.MessageType.REPLY,
    #     0,
    # )
    # r2 = utlis.unmarshal(replyMarshal)
    # # print(r2.error)
    # for value in r2.value:
    #     print(
    #         "Arrival Time:",
    #         value.arrivalTime,
    #     )

    requestMarshal, _ = utlis.marshal(
        utlis.CancellationRequest(643),
        utlis.ServiceType.CANCALLATION,
        utlis.MessageType.REQUEST,
        0,
    )
    r1 = utlis.unmarshal(requestMarshal)
    print("Flight ID:", r1[0].flightId)

    replyMarshal, _ = utlis.marshal(
        utlis.Response(
            [
                utlis.CancellationResponse("Cancelled!!"),
            ]
        ),
        utlis.ServiceType.CANCALLATION,
        utlis.MessageType.REPLY,
        0,
    )
    r2 = utlis.unmarshal(replyMarshal)
    # print(r2.error)
    for value in r2.value:
        print(
            "Msg:",
            value.msg,
        )

    # bytes, size = utlis.marshal(
    #     utlis.Response(error="This is a very long error message!"),
    #     # utlis.Response(
    #     #     [
    #     #         utlis.QueryFlightIdResponse(4510),
    #     #         utlis.QueryFlightIdResponse(24),
    #     #         utlis.QueryFlightIdResponse(421),
    #     #         utlis.QueryFlightIdResponse(755),
    #     #     ]
    #     # ),
    #     utlis.ServiceType.QUERY_FLIGHTID,
    #     utlis.MessageType.REPLY,
    #     # 0,
    #     1,
    # )

    bytes, size = utlis.marshal(
        utlis.ReservationRequest(554, 2),
        utlis.ServiceType.RESERVATION,
        utlis.MessageType.REQUEST,
        0,
    )

    replyBytes = bytearray()
    replyBytes.extend(requestId)
    replyBytes.extend(bytes)

    print("The size with request ID is", len(replyBytes))
    print("The size is", size)
    print(" ".join(hex(x) for x in bytes))
    s.sendto(replyBytes, address)
    # break

    # print("\n\n 2. Server received: ", request[1].source,
    #       request[1].destination, "\n\n")
    # print("\n\n 2. Server received: ", request.source,
    #       request.destination, "\n\n")
    # print("\n\n 2. Server received: ", data.decode('utf-8'), "\n\n")
    # send_data = input("Type some text to send => ")
    # s.sendto(send_data.encode("utf-8"), address)
    # print("\n\n 1. Server sent : ", send_data, "\n\n")
