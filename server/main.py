import socket
import sys
import utlis
import csv

ip = "127.0.0.1"
port = 8080
<<<<<<< Updated upstream
=======
s = None
delay = 30

reservation = {}
# monitorCache = {}
monitorCache = []


# def set_cache(key, value, timeout):
#     """Adds a key-value pair to the cache with a timeout."""
#     monitorCache[key] = value
#     # Create a new thread that waits for the timeout and deletes the key from the cache.
#     t = threading.Timer(timeout, delete_cache, args=[key])
#     t.start()


# def get_cache(key):
#     """Retrieves a value from the cache."""
#     return monitorCache.get(key)


# def delete_cache(key):
#     """Deletes a key from the cache."""
#     if key in monitorCache:
#         del monitorCache[key]


def get_cache(key):
    # Check if the key is present in the cache and not expired
    if monitorCache[key]["expiry"] > time.time():
        return monitorCache[key]["value"]
    elif monitorCache[key]["expiry"] <= time.time():
        del monitorCache[key]
        return None
    else:
        return None


def set_cache(key, value, expiry_time):
    # Add the key-value pair to the cache with the expiry time
    # monitorCache[key] = {"value": value, "expiry": time.time() + expiry_time}
    monitorCache.append({"value": value, "expiry": time.time() + expiry_time})


def monitor_flight(address, flightID, requestId, monitorInterval):
    global monitorCache

    response = utlis.Response()
    errorCode = 0

    selected_flights = df[(df["FlightID"] == flightID)]
    selected_flights = selected_flights.reset_index()

    if len(selected_flights.index == 0):
        length = len(monitorCache)
        set_cache(length, {flightID: (address, requestId)}, monitorInterval * 60)
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
>>>>>>> Stashed changes

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (ip, port)
s.bind(server_address)
print("Do Ctrl+c to exit the program !!")

def search_flights(source, destination):
    arrayofIDs = []
    with open('flight records.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['From'] == source and row['To'] == destination:
                arrayofIDs.append(int(row['FlightID']))
    return arrayofIDs

def get_flights_details(flightIDs):
    arrayofDetails = []
    with open('flight records.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for id in flightIDs:
                if row['FlightID'] == id:
                    arrayofDetails.append(row['DepartTime'])
                    arrayofDetails.append(row['Airfare'])
                    arrayofDetails.append(row['NumSeat'])

    print(arrayofDetails)
    return arrayofDetails

def ReserveSeat(flightIDs, Seat):
    with open('flight records.csv', newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for id in flightIDs:
                if row['FlightID'] == id:
                    row['NumSeat'] = int(row['NumSeat']) - Seat
                    RemendingSeat = row['NumSeat']
    
    return RemendingSeat

while True:
    print("####### Server is listening #######")
    data, address = s.recvfrom(4096)
    print(data)
    request = utlis.unmarshal(data)

<<<<<<< Updated upstream
    choice = input("What is the choice: ")

    if choice == "1":  
        print("\nServer received: ", request[0].source, request[0].destination, "\n")
        source = request[0].source
        destination = request[0].destination
        print(source, destination)
        arrayofIDs = search_flights(source, destination)
        print(arrayofIDs)
        if(arrayofIDs != []):
            print('found')
            bytes, size = utlis.marshal(
            utlis.QueryFlightIdResponse(arrayofIDs, ""),
            utlis.ServiceType.QUERY_FLIGHTID,
            utlis.MessageType.REPLY,
            0,
=======
    time.sleep(30)
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
    print("the len is: " + str(len(selectedFlight)))

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
>>>>>>> Stashed changes
            )
        else:
            print('not found')
            bytes, size = utlis.marshal(
            utlis.QueryFlightIdResponse([],error="not found"),
            utlis.ServiceType.QUERY_FLIGHTID,
            utlis.MessageType.REPLY,
            0
        )
    elif choice == "2" :
        flightIDs = input("Enter your ID: ")
        #flightIDs = request
        arrayofDetails = get_flights_details(flightIDs)
    elif choice == "3":
        flightIDs = input("Enter your flight ID: ")
        Seatnum = int(input("Enter number of seat to reserve: "))
        ReserveSeat(flightIDs, Seatnum)

        

    #print("The size is ", size)
    print(bytes)
    #s.sendto(bytes, address)
