import socket
import sys
import time
import utlis
import csv
import pandas as pd

df = None
ip = "127.0.0.1"
port = 8080

reservation = {}


def start_server():
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    print("Do Ctrl+c to exit the program !!")

    return s


def load_flight_info():
    global df
    df = pd.read_csv("flightInfo.csv")


def search_flights(source, destination):
    response = utlis.Response()
    errorCode = 0

    # Use boolean indexing to select the rows that match your criteria
    selected_flights = df[(df["From"] == source) & (df["To"] == destination)]

    # Get the FlightID column from the selected rows
    flightIds = list(map(int, selected_flights["FlightID"].values.astype(int)))

    print(flightIds)
    if len(flightIds) != 0:
        response.value = [utlis.QueryFlightIdResponse() for i in range(len(flightIds))]
        for i in range(len(flightIds)):
            response.value[i].flightId = flightIds[i]
    else:
        response = utlis.Response(
            error="No flights from " + source + " to " + destination + " was found."
        )
        errorCode = 0

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_FLIGHTID,
        utlis.MessageType.REPLY,
        errorCode,
    )
    return bytes, size


def get_flights_details(flightID):
    response = utlis.Response()
    errorCode = 0

    selected_flights = df[(df["FlightID"] == flightID)]
    selected_flights = (
        selected_flights.reset_index()
    )  # make sure indexes pair with number of rows

    if len(selected_flights.index == 0):
        response.value = [
            utlis.QueryDepartureTimeResponse()
            for i in range(len(selected_flights.index))
        ]

        for i, row in selected_flights.iterrows():
            response.value[i].departureTime = time.strptime(
                row["DepartTime"], "%d/%m/%Y %H:%M"
            )
            response.value[i].airFare = row["Airfare"]
            response.value[i].seatAvailability = row["NumSeat"]
    else:
        response = utlis.Response(error="Flight ID " + str(flightID) + " not found.")
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_DEPARTURETIME,
        utlis.MessageType.REPLY,
        errorCode,
    )
    return bytes, size


def reserve_seat(ip, flightID, seat):
    global df
    global reservation

    response = utlis.Response()
    errorCode = 0
    selectedFlight = df[(df["FlightID"] == flightID)]
    noSeat = selectedFlight["NumSeat"]

    if len(selectedFlight) == 1 and len(noSeat) == 1 and seat <= int(noSeat.values[0]):
        df.loc[df["FlightID"] == flightID, "NumSeat"] -= seat

        if ip in reservation:
            if flightID in reservation[ip]:
                reservation[ip][flightID] += seat
            else:
                reservation[ip][flightID] = seat
        else:
            reservation[ip] = {flightID: seat}
        response = utlis.Response([utlis.ReservationResponse("Seats Reversed")])
    elif len(selectedFlight) == 0:
        response = utlis.Response(error="Flight ID " + str(flightID) + " not found.")
        errorCode = 1
    elif len(selectedFlight) > 1:
        response = utlis.Response(error="Server Error.")
        errorCode = 1
    elif seat > int(noSeat.values[0]):
        response = utlis.Response(
            error="Flight ID " + str(flightID) + " have not enough seats."
        )
        errorCode = 1
    else:
        response = utlis.Response(error="Server Error.")
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.RESERVATION,
        utlis.MessageType.REPLY,
        errorCode,
    )
    return bytes, size


def check_reservation(ip, flightID):
    response = utlis.Response()
    errorCode = 0

    if ip in reservation:
        if flightID in reservation[ip]:
            seat = reservation[ip][flightID]
            response = utlis.Response([utlis.CheckReservationResponse(seat)])
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID " + str(flightID) + " not found."
            )
            errorCode = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flightID) + " not found."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.CHECK_RESERVATION,
        utlis.MessageType.REPLY,
        errorCode,
    )
    return bytes, size


def cancel_reservation(ip, flightID):
    global df
    global reservation

    response = utlis.Response()
    errorCode = 0

    if ip in reservation:
        if flightID in reservation[ip]:
            seat = reservation[ip][flightID]
            df.loc[df["FlightID"] == flightID, "NumSeat"] += seat
            del reservation[ip][flightID]
            print("Deleted")
            response = utlis.Response(
                [
                    utlis.CancellationResponse(
                        "Seats reservation for Flight ID "
                        + str(flightID)
                        + " is cancelled"
                    )
                ]
            )
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID " + str(flightID) + " not found."
            )
            errorCode = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flightID) + " not found."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.CANCELLATION,
        utlis.MessageType.REPLY,
        errorCode,
    )
    return bytes, size


def main():
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)
        print(data)
        print(address[0])
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
            bytes, size = reserve_seat(address[0], flightID, Seatnum)
            print(reservation)
        elif serviceType == 4:
            flightID = request[0].flightId
            bytes, size = check_reservation(address[0], flightID)
            print(reservation)
        elif serviceType == 5:
            flightID = request[0].flightId
            bytes, size = cancel_reservation(address[0], flightID)
            print(reservation)

        print(bytes)

        replyBytes = bytearray()
        replyBytes.extend(requestId)
        replyBytes.extend(bytes)
        s.sendto(replyBytes, address)
        # break


if __name__ == "__main__":
    main()
