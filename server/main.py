import socket
import sys
import threading
import time
import utlis
import csv
import pandas as pd

df = None
ip = "127.0.0.1"
# ip = "10.0.0.12"
port = 8080
s = None

reservation = {}
monitorCache = []

requestIds = set()
requestExpiry = {}
responseCache = {}

def start_cache_cleaner(interval):
    print("CLEANING")
    def clean_cache():
        while True:
            expired_keys = []
            for key in responseCache:
                if responseCache[key]["expiry"] <= time.time():
                    expired_keys.append(key)
            for key in expired_keys:
                del responseCache[key]
            time.sleep(interval)
    t = threading.Thread(target=clean_cache)
    t.daemon = True
    t.start()

start_cache_cleaner(60)  # Run every 60 seconds


def get_response_cache(key):
    if key in responseCache:
        return responseCache[key]["value"]
    else:
        return None
    
# def get_response_cache(key):
#     if responseCache[key]["expiry"] > time.time():
#         return responseCache[key]["value"]
#     elif responseCache[key]["expiry"] <= time.time():
#         del responseCache[key]
#         return None
#     else:
#         return None


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


def monitor_flight(address, flightID, requestId, monitorInterval):
    global monitorCache

    response = utlis.Response()
    errorCode = 0

    selected_flights = df[(df["FlightID"] == flightID)]
    selected_flights = selected_flights.reset_index()

    if len(selected_flights.index == 0):
        set_cache({flightID: (address, requestId)}, monitorInterval * 60)
        response = utlis.Response(
            [utlis.MonitorResponse("Monitoring started succesfully!")]
        )
    else:
        response = utlis.Response(
            error="The flight ID "
            + str(flightID)
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


def send_updates(flightID):
    global monitorCache
    length = len(monitorCache)
    print("Sending Updates")
    print("length:", length)
    print("monitorCache:", monitorCache)

    index = 0
    for _ in range(length):
        val = get_cache(index)
        print("val", val)
        if val != None:
            index += 1
            if flightID in val:
                address = val[flightID][0]
                requestId = val[flightID][1]
                seats = df.loc[df["FlightID"] == flightID, "NumSeat"].iloc[0]
                print("address:", address)
                print("requestId:", requestId)
                print("seats:", seats)

                bytes, size = utlis.marshal(
                    utlis.Response(
                        [
                            utlis.MonitorResponse(
                                "FlightId "
                                + str(flightID)
                                + " updated to "
                                + str(seats)
                            )
                        ]
                    ),
                    utlis.ServiceType.MONITOR,
                    utlis.MessageType.REPLY,
                    0,
                    0,
                )
                replyBytes = bytearray()
                replyBytes.extend(requestId)
                replyBytes.extend(bytes)
                s.sendto(replyBytes, address)


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
    print(len(flightIds))

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
        0,
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

        send_updates(flightID)
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
        0,
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
        0,
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
            send_updates(flightID)
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
        0,
    )
    return bytes, size


def at_most_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        #print("Current Stored Respond: \n", responseCache)
        #print("Current Stored Address ID: \n", requestIds)
        data, address = s.recvfrom(4096)
        requestId = data[:23]
        ip = utlis.decodeIPFromRequestId(requestId)
        print("Data:", data)
        print("IP:", ip)
        print(len(ip))

        duplicated = check_duplicated_requestIds(requestId)
        requestByte = data[23:]
        request, serviceType, _, packetLoss = utlis.unmarshal(requestByte)

        print(df.to_string())
        print("Service Type:", serviceType)
        print("Time Out:", packetLoss)

        if not duplicated:
            if serviceType == 0:
                print(
                    "\nServer received: ",
                    request[0].source,
                    request[0].destination,
                    "\n",
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
                bytes, size = reserve_seat(ip, flightID, Seatnum)
            elif serviceType == 3:
                flightID = request[0].flightId
                monitorInterval = request[0].monitorInterval
                bytes, size = monitor_flight(
                    address, flightID, requestId, monitorInterval
                )
            elif serviceType == 4:
                flightID = request[0].flightId
                bytes, size = check_reservation(ip, flightID)
            elif serviceType == 5:
                flightID = request[0].flightId
                bytes, size = cancel_reservation(ip, flightID)

            set_response_cache(requestId, bytes, 2 * 60)

            if not packetLoss:
                replyBytes = bytearray()
                replyBytes.extend(requestId)
                replyBytes.extend(bytes)
                s.sendto(replyBytes, address)
        else:
            bytes = get_response_cache(requestId)

            if not packetLoss:
                replyBytes = bytearray()
                replyBytes.extend(requestId)
                replyBytes.extend(bytes)
                s.sendto(replyBytes, address)


def at_least_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)
        requestId = data[:23]
        ip = utlis.decodeIPFromRequestId(requestId)
        print("Data:", data)
        print("IP:", ip)
        print(len(ip))

        requestByte = data[23:]
        request, serviceType, _, packetLoss = utlis.unmarshal(requestByte)

        print(df.to_string())
        print("Service Type:", serviceType)
        print("Time Out:", packetLoss)

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
            bytes, size = reserve_seat(ip, flightID, Seatnum)
        elif serviceType == 3:
            flightID = request[0].flightId
            monitorInterval = request[0].monitorInterval
            bytes, size = monitor_flight(address, flightID, requestId, monitorInterval)
        elif serviceType == 4:
            flightID = request[0].flightId
            bytes, size = check_reservation(ip, flightID)
        elif serviceType == 5:
            flightID = request[0].flightId
            bytes, size = cancel_reservation(ip, flightID)

        if not packetLoss:
            replyBytes = bytearray()
            replyBytes.extend(requestId)
            replyBytes.extend(bytes)
            s.sendto(replyBytes, address)
        # break


if __name__ == "__main__":
    if len(sys.argv) == 2:
        choice = sys.argv[1]
    else:
        print("Run like : python3 main.py <choice>")
        exit(1)

    if choice == "1":
        at_most_once()
    elif choice == "2":
        at_least_once()
