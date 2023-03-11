import socket
import sys
import threading
import time
import utlis
import pandas as pd
from tabulate import tabulate

ip = "127.0.0.1"
# ip = "10.0.0.12"
port = 8080
s = None

df = None

reservation = {}

monitorCache = []

requestIds = set()
requestExpiry = {}
responseCache = {}

Services = [
    "Look for available flights",
    "Get flight details",
    "Make seat reservation",
    "Monitor flight",
    "Check seat reservation",
    "Cancel seat reservation",
]


def start_server():
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    print("####### Server Started! #######")

    return s


def load_flight_info():
    global df
    df = pd.read_csv("flightInfo.csv")

    print("####### Initial Flight Information #######")
    print(tabulate(df, headers="keys", tablefmt="psql"))


def start_cache_cleaner(interval):
    def clean_cache():
        while True:
            expired_keys = []
            for key in responseCache:
                if responseCache[key]["expiry"] <= time.time():
                    expired_keys.append(key)
            for key in expired_keys:
                del responseCache[key]
            print("####### Clearing saved responses #######")
            print("Updated saved Responses:", responseCache)
            print("####### Clearing Ended #######")
            time.sleep(interval)

    t = threading.Thread(target=clean_cache)
    t.daemon = True
    t.start()


def get_response_cache(key):
    if key in responseCache:
        return responseCache[key]["value"]
    else:
        return None


def set_response_cache(key, value, expiry_time):
    responseCache[key] = {"value": value, "expiry": time.time() + expiry_time}


def check_duplicated_requestIds(requestId):
    # Remove expired request IDs from the set.
    for expired_id in [k for k, v in requestExpiry.items() if v <= time.time()]:
        requestIds.remove(expired_id)
        del requestExpiry[expired_id]

    if requestId not in requestIds:
        requestIds.add(requestId)
        requestExpiry[requestId] = time.time() + 2 * 60
        return False
    else:
        return True


def get_cache(index):
    if monitorCache[index]["expiry"] > time.time():
        return monitorCache[index]["value"]
    elif monitorCache[index]["expiry"] <= time.time():
        del monitorCache[index]
        return None
    else:
        return None


def set_cache(value, expiry_time):
    monitorCache.append({"value": value, "expiry": time.time() + expiry_time})


def send_updates(flightId):
    global monitorCache
    length = len(monitorCache)

    index = 0
    for _ in range(length):
        val = get_cache(index)
        if val != None:
            index += 1
            if flightId in val:
                address = val[flightId][0]
                requestId = val[flightId][1]
                seats = df.loc[df["FlightID"] == flightId, "NumSeat"].iloc[0]

                bytes, size = utlis.marshal(
                    utlis.Response(
                        [
                            utlis.MonitorResponse(
                                "Flight ID "
                                + str(flightId)
                                + " updated to "
                                + str(seats)
                                + "."
                            )
                        ]
                    ),
                    utlis.ServiceType.MONITOR,
                    utlis.MessageType.REPLY,
                    0,
                    0,
                )
                send_response(address, requestId, bytes, 0)


def search_flights(source, destination):
    response = utlis.Response()
    errorCode = 0

    # Use boolean indexing to select the rows that match your criteria
    selected_flights = df[(df["From"] == source) & (df["To"] == destination)]

    # Get the FlightID column from the selected rows
    flightIds = list(map(int, selected_flights["FlightID"].values.astype(int)))

    if len(flightIds) > 0:
        response.value = [utlis.QueryFlightIdResponse() for i in range(len(flightIds))]
        for i in range(len(flightIds)):
            response.value[i].flightId = flightIds[i]
    else:
        response = utlis.Response(
            error="No flights from " + source + " to " + destination + " was found."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_FLIGHTID,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def get_flights_details(flightId):
    response = utlis.Response()
    errorCode = 0

    selected_flights = df[(df["FlightID"] == flightId)]
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
        response = utlis.Response(error="Flight ID " + str(flightId) + " not found.")
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_DEPARTURETIME,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def reserve_seat(ip, flightId, seat):
    global df
    global reservation

    response = utlis.Response()
    errorCode = 0
    selectedFlight = df[(df["FlightID"] == flightId)]
    noOfSeats = selectedFlight["NumSeat"]

    if (
        len(selectedFlight) == 1
        and len(noOfSeats) == 1
        and seat <= int(noOfSeats.values[0])
    ):
        df.loc[df["FlightID"] == flightId, "NumSeat"] -= seat
        if ip in reservation:

            if flightId in reservation[ip]:
                reservation[ip][flightId] += seat
            else:
                reservation[ip][flightId] = seat
        else:
            reservation[ip] = {flightId: seat}

        send_updates(flightId)
        response = utlis.Response([utlis.ReservationResponse("Seats Reversed")])
    elif len(selectedFlight) == 0:
        response = utlis.Response(error="Flight ID " + str(flightId) + " not found.")
        errorCode = 1
    elif len(selectedFlight) > 1:
        response = utlis.Response(error="Server Error. There is duplicated Flight ID")
        errorCode = 1
    elif seat > int(noOfSeats.values[0]):
        response = utlis.Response(
            error="Flight ID " + str(flightId) + " have not enough seats."
        )
        errorCode = 1
    else:
        response = utlis.Response(
            error="Server Error. Something is wrong with the flight information"
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.RESERVATION,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def monitor_flight(address, flightId, requestId, monitorInterval):
    global monitorCache

    response = utlis.Response()
    errorCode = 0

    selected_flights = df[(df["FlightID"] == flightId)]
    selected_flights = selected_flights.reset_index()

    if len(selected_flights.index == 0):
        set_cache({flightId: (address, requestId)}, monitorInterval * 60)
        response = utlis.Response(
            [utlis.MonitorResponse("Monitoring started succesfully!")]
        )
    else:
        response = utlis.Response(
            error="The flight ID "
            + str(flightId)
            + " you are trying to monitor doesn't exist."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.MONITOR,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def check_reservation(ip, flightId):
    response = utlis.Response()
    errorCode = 0

    if ip in reservation:
        if flightId in reservation[ip]:
            seat = reservation[ip][flightId]
            response = utlis.Response([utlis.CheckReservationResponse(seat)])
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID "
                + str(flightId)
                + " was not found."
            )
            errorCode = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flightId) + " was not found."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.CHECK_RESERVATION,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def cancel_reservation(ip, flightId):
    global df
    global reservation

    response = utlis.Response()
    errorCode = 0

    if ip in reservation:
        if flightId in reservation[ip]:
            seat = reservation[ip][flightId]
            df.loc[df["FlightID"] == flightId, "NumSeat"] += seat
            del reservation[ip][flightId]
            send_updates(flightId)
            response = utlis.Response(
                [
                    utlis.CancellationResponse(
                        "Seat reservation for Flight ID "
                        + str(flightId)
                        + " is cancelled"
                    )
                ]
            )
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID "
                + str(flightId)
                + " was not found."
            )
            errorCode = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flightId) + " was not found."
        )
        errorCode = 1

    bytes, size = utlis.marshal(
        response,
        utlis.ServiceType.CANCELLATION,
        utlis.MessageType.REPLY,
        errorCode,
        0,
    )
    return bytes, size


def services(request, serviceType, address, requestId):
    print("For Service:", Services[serviceType])
    print("Request Parameters")

    if serviceType == 0:
        source = request[0].source.lower()
        destination = request[0].destination.lower()
        print("Source:", source, "Destination:", destination)

        bytes, size = search_flights(source, destination)
    elif serviceType == 1:
        flightId = request[0].flightId
        print("Flight ID:", flightId)

        bytes, size = get_flights_details(flightId)
    elif serviceType == 2:
        flightId = request[0].flightId
        noOfSeats = request[0].noOfSeats

        print("Flight ID:", flightId, "No. of seats:", noOfSeats)
        bytes, size = reserve_seat(ip, flightId, noOfSeats)
    elif serviceType == 3:
        flightId = request[0].flightId
        monitorInterval = request[0].monitorInterval

        print("Flight ID:", flightId, "Monitor Interval:", monitorInterval)
        bytes, size = monitor_flight(address, flightId, requestId, monitorInterval)
    elif serviceType == 4:
        flightId = request[0].flightId

        print("Flight ID:", flightId)
        bytes, size = check_reservation(ip, flightId)
    elif serviceType == 5:
        flightId = request[0].flightId

        print("Flight ID:", flightId)
        bytes, size = cancel_reservation(ip, flightId)

    print("Updated Flights Information")
    print(tabulate(df, headers="keys", tablefmt="psql"))
    return bytes, size


def decode_request(data):
    requestId = data[:23]
    ip = utlis.decodeIPFromRequestId(requestId)
    requestByte = data[23:]
    request, serviceType, _, packetLoss = utlis.unmarshal(requestByte)

    print("Received request from:", ip)
    print("Simulated packet loss:", bool(packetLoss))
    return requestId, ip, request, serviceType, packetLoss


def send_response(address, requestId, bytes, packetLoss):
    if not packetLoss:
        replyBytes = bytearray()
        replyBytes.extend(requestId)
        replyBytes.extend(bytes)
        s.sendto(replyBytes, address)


def at_most_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)

        requestId, ip, request, serviceType, packetLoss = decode_request(data)
        duplicated = check_duplicated_requestIds(requestId)
        print("Saved Request IDs:", requestIds)

        print("Duplicated Request:", bool(duplicated))
        if not duplicated:
            bytes, size = services(request, serviceType, address, requestId)

            set_response_cache(requestId, bytes, 2 * 60)
            print("Saved Responses:", responseCache)
        else:
            bytes = get_response_cache(requestId)

        send_response(address, requestId, bytes, packetLoss)


def at_least_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)

        requestId, ip, request, serviceType, packetLoss = decode_request(data)

        bytes, size = services(request, serviceType, address, requestId)
        send_response(address, requestId, bytes, packetLoss)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        choice = sys.argv[1]
    else:
        print("Run like : python3 main.py <choice[1: At Most Once, 2: At Least Once]>")
        exit(1)

    if choice == "1":
        start_cache_cleaner(60)  # Run every 60 seconds
        at_most_once()
    elif choice == "2":
        at_least_once()
    else:
        print("Run like : python3 main.py <choice[1: At Most Once, 2: At Least Once]>")
        exit(1)
