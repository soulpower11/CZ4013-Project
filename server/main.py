import socket
import sys
import time
import utlis
import csv
import pandas as pd

df = None

ip = "127.0.0.1"
port = 8080

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (ip, port)
s.bind(server_address)
print("Do Ctrl+c to exit the program !!")


def load_flight_info():
    global df
    df = pd.read_csv("flightInfo.csv")


def search_flights(source, destination):
    # Use boolean indexing to select the rows that match your criteria
    selected_flights = df[(df["From"] == source) & (df["To"] == destination)]

    # Get the FlightID column from the selected rows
    flightIds = list(map(int, selected_flights["FlightID"].values.astype(int)))

    print(flightIds)
    if len(flightIds) != 0:
        print("found")
        queryResponse = utlis.Response()
        queryResponse.value = [
            utlis.QueryFlightIdResponse() for i in range(len(flightIds))
        ]
        for i in range(len(flightIds)):
            queryResponse.value[i].flightId = flightIds[i]

        bytes, size = utlis.marshal(
            queryResponse,
            utlis.ServiceType.QUERY_FLIGHTID,
            utlis.MessageType.REPLY,
            0,
        )
    else:
        print("not found")
        bytes, size = utlis.marshal(
            utlis.Response(
                error="No flights from " + source + " to " + destination + " was found."
            ),
            utlis.ServiceType.QUERY_FLIGHTID,
            utlis.MessageType.REPLY,
            1,
        )
    return bytes, size


def get_flights_details(flightID):
    selected_flights = df[(df["FlightID"] == flightID)]
    selected_flights = (
        selected_flights.reset_index()
    )  # make sure indexes pair with number of rows

    if len(selected_flights.index == 0):
        queryResponse = utlis.Response()
        queryResponse.value = [
            utlis.QueryDepartureTimeResponse()
            for i in range(len(selected_flights.index))
        ]

        for i, row in selected_flights.iterrows():
            queryResponse.value[i].departureTime = time.strptime(
                row["DepartTime"], "%d/%m/%Y %H:%M"
            )
            queryResponse.value[i].airFare = row["Airfare"]
            queryResponse.value[i].seatAvailability = row["NumSeat"]

        bytes, size = utlis.marshal(
            queryResponse,
            utlis.ServiceType.QUERY_DEPARTURETIME,
            utlis.MessageType.REPLY,
            0,
        )
    else:
        bytes, size = utlis.marshal(
            utlis.Response(error="Flight ID " + str(flightID) + " not found."),
            utlis.ServiceType.QUERY_DEPARTURETIME,
            utlis.MessageType.REPLY,
            1,
        )

    return bytes, size


def ReserveSeat(flightID, seat):
    global df
    # check if Flight ID equals 1 and Num Seats is not less than decrement value
    selectedFlight = df[(df["FlightID"] == flightID)]
    noSeat = selectedFlight["NumSeat"]

    if len(selectedFlight) == 1 and len(noSeat) == 1 and seat <= int(noSeat.values[0]):
        # decrement value
        df.loc[df["FlightID"] == flightID, "NumSeat"] -= seat
        bytes, size = utlis.marshal(
            utlis.Response([utlis.ReservationResponse("Seats Reversed")]),
            utlis.ServiceType.RESERVATION,
            utlis.MessageType.REPLY,
            0,
        )
    elif len(selectedFlight) == 0:
        bytes, size = utlis.marshal(
            utlis.Response(error="Flight ID " + str(flightID) + " not found."),
            utlis.ServiceType.RESERVATION,
            utlis.MessageType.REPLY,
            1,
        )
    elif len(selectedFlight) > 1:
        bytes, size = utlis.marshal(
            utlis.Response(error="Server Error."),
            utlis.ServiceType.RESERVATION,
            utlis.MessageType.REPLY,
            1,
        )
    elif seat > int(noSeat.values[0]):
        bytes, size = utlis.marshal(
            utlis.Response(
                error="Flight ID " + str(flightID) + " have not enough seats."
            ),
            utlis.ServiceType.RESERVATION,
            utlis.MessageType.REPLY,
            1,
        )
    else:
        bytes, size = utlis.marshal(
            utlis.Response(error="Server Error."),
            utlis.ServiceType.RESERVATION,
            utlis.MessageType.REPLY,
            1,
        )

    return bytes, size


def main():
    load_flight_info()
    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)
        print(data)
        requestId = data[:20]
        requestByte = data[20:]
        request, serviceType, _ = utlis.unmarshal(requestByte)
        print(df.to_string())

        print(serviceType)

        if serviceType == 0:
            print(
                "\nServer received: ", request[0].source, request[0].destination, "\n"
            )
            source = request[0].source.lower()
            destination = request[0].destination.lower()
            print(source, destination)
            bytes, size = search_flights(source, destination)
        elif serviceType == 1:
            flightId = request[0].flightId
            bytes, size = get_flights_details(flightId)
        elif serviceType == 2:
            flightID = request[0].flightId
            Seatnum = request[0].noOfSeats
            bytes, size = ReserveSeat(flightID, Seatnum)
            print(df.to_string())

        print(bytes)

        replyBytes = bytearray()
        replyBytes.extend(requestId)
        replyBytes.extend(bytes)
        s.sendto(replyBytes, address)
        # break


if __name__ == "__main__":
    main()
