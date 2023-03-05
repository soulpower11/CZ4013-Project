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

    # bytes, size = utlis.marshal(
    #     utlis.QueryFlightIdRequest("Singapore", "Malaysia"),
    #     utlis.ServiceType.QUERY_FLIGHTID,
    #     utlis.MessageType.REQUEST,
    #     0,
    # )
    bytes, size = utlis.marshal(
        utlis.QueryFlightIdResponse([102, 222, 555], "error!!!"),
        utlis.ServiceType.QUERY_FLIGHTID,
        utlis.MessageType.REPLY,
        1,
    )

    replyBytes = bytearray()
    replyBytes.extend(requestId)
    replyBytes.extend(bytes)
    print(len(replyBytes))

    print("The size is ", size)
    print(bytes)
    s.sendto(replyBytes, address)
    break

    # print("\n\n 2. Server received: ", request[1].source,
    #       request[1].destination, "\n\n")
    # print("\n\n 2. Server received: ", request.source,
    #       request.destination, "\n\n")
    # print("\n\n 2. Server received: ", data.decode('utf-8'), "\n\n")
    # send_data = input("Type some text to send => ")
    # s.sendto(send_data.encode("utf-8"), address)
    # print("\n\n 1. Server sent : ", send_data, "\n\n")
