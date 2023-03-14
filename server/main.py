import socket
import sys
import threading
import time
import utlis
import pandas as pd
from tabulate import tabulate

# Server IP, Port and Object
ip = "127.0.0.1"
# ip = "10.0.0.12"
port = 8080
s = None

# Flight Info Dataframe
df = None

# Save the reservations
reservation = {}

# Save the monitoring client address
monitorCache = []

# Save the request ids and response
requestIds = set()
requestExpiry = {}
responseCache = {}

# The services name
Services = [
    "Look for available flights",
    "Get flight details",
    "Make seat reservation",
    "Monitor flight",
    "Check seat reservation",
    "Cancel seat reservation",
]


# Start the UDP server
def start_server():
    # Create a UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    server_address = (ip, port)
    s.bind(server_address)
    print("####### Server Started! #######")

    return s


# Load flight info from CSV
def load_flight_info():
    global df
    df = pd.read_csv("flightInfo.csv")

    print("####### Initial Flight Information #######")
    print(tabulate(df, headers="keys", tablefmt="psql"))


# Clear the response cache, runs every 1 min
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


# Get the response cache
# For at most once operation
def get_response_cache(key):
    if key in responseCache:
        return responseCache[key]["value"]
    else:
        return None


# Set the response cache
# For at most once operation
def set_response_cache(key, value, expiry_time):
    responseCache[key] = {"value": value, "expiry": time.time() + expiry_time}


# Check for duplicated request ids add it to the set
# For at most once operation
def check_duplicated_request_ids(request_id):
    # Remove expired request IDs from the set.
    for expired_id in [k for k, v in requestExpiry.items() if v <= time.time()]:
        requestIds.remove(expired_id)
        del requestExpiry[expired_id]

    if request_id not in requestIds:
        requestIds.add(request_id)
        requestExpiry[request_id] = time.time() + 2 * 60
        return False
    else:
        return True


# Get the address for the monitoring client
def get_cache(index):
    if monitorCache[index]["expiry"] > time.time():
        return monitorCache[index]["value"]
    elif monitorCache[index]["expiry"] <= time.time():
        del monitorCache[index]
        return None
    else:
        return None


# Set the monitoring cache
def set_cache(value, expiry_time):
    monitorCache.append({"value": value, "expiry": time.time() + expiry_time})


# Send update to client that is subscribed to monitor flight
def send_updates(flight_id):
    global monitorCache
    length = len(monitorCache)

    index = 0
    # Iterate through the monitor cache, remove expired ones and send updates to the correct ones
    for _ in range(length):
        val = get_cache(index)
        if val != None:
            index += 1
            if flight_id in val:
                address = val[flight_id][0]
                request_id = val[flight_id][1]
                seats = df.loc[df["FlightID"] == flight_id, "NumSeat"].iloc[
                    0
                ]  # Get the number of seats of the Flight ID

                # Marshal the response and send it back to the client
                bytes_, size = utlis.marshal(
                    utlis.Response(
                        [
                            utlis.MonitorResponse(
                                "Flight ID "
                                + str(flight_id)
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
                send_response(address, request_id, bytes_, 0)


# The query Flight ID feature
# Get the Flight IDs by specifying the source and destination country
def search_flights(source, destination):
    response = utlis.Response()
    error_code = 0

    # Use boolean indexing to select the rows that match your criteria
    selected_flights = df[(df["From"] == source) & (df["To"] == destination)]

    # Get the FlightID column from the selected rows
    flight_ids = list(map(int, selected_flights["FlightID"].values.astype(int)))

    if len(flight_ids) > 0:
        response.value = [utlis.QueryFlightIdResponse() for i in range(len(flight_ids))]
        for i in range(len(flight_ids)):
            response.value[i].flightId = flight_ids[i]
    else:
        response = utlis.Response(
            error="No flights from " + source + " to " + destination + " was found."
        )
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_FLIGHT_ID,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# The query flight details feature
# Get the departure time, airfare and seat availability of a specific Flight ID
def get_flights_details(flight_id):
    response = utlis.Response()
    error_code = 0

    selected_flights = df[(df["FlightID"] == flight_id)]
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
        response = utlis.Response(error="Flight ID " + str(flight_id) + " not found.")
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.QUERY_DEPARTURE_TIME,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# The reservation function
# Reserve seats for a specific Flight ID
def reserve_seat(ip, flight_id, seat):
    global df
    global reservation

    response = utlis.Response()
    error_code = 0
    selected_flight = df[(df["FlightID"] == flight_id)]
    no_of_seats = selected_flight["NumSeat"]

    if (
        len(selected_flight) == 1
        and len(no_of_seats) == 1
        and seat <= int(no_of_seats.values[0])
    ):
        df.loc[df["FlightID"] == flight_id, "NumSeat"] -= seat
        if ip in reservation:

            if flight_id in reservation[ip]:
                reservation[ip][flight_id] += seat
            else:
                reservation[ip][flight_id] = seat
        else:
            reservation[ip] = {flight_id: seat}

        send_updates(flight_id)
        response = utlis.Response([utlis.ReservationResponse("Seats Reversed")])
    elif len(selected_flight) == 0:
        response = utlis.Response(error="Flight ID " + str(flight_id) + " not found.")
        error_code = 1
    elif len(selected_flight) > 1:
        response = utlis.Response(error="Server Error. There is duplicated Flight ID")
        error_code = 1
    elif seat > int(no_of_seats.values[0]):
        response = utlis.Response(
            error="Flight ID " + str(flight_id) + " have not enough seats."
        )
        error_code = 1
    else:
        response = utlis.Response(
            error="Server Error. Something is wrong with the flight information"
        )
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.RESERVATION,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# The monitor feature
# Monitor the seats availability of a specific flight
def monitor_flight(address, flight_id, request_id, monitor_interval):
    global monitorCache

    response = utlis.Response()
    error_code = 0

    selected_flights = df[(df["FlightID"] == flight_id)]
    selected_flights = selected_flights.reset_index()

    if len(selected_flights.index == 0):
        set_cache({flight_id: (address, request_id)}, monitor_interval * 60)
        response = utlis.Response(
            [utlis.MonitorResponse("Monitoring started successfully!")]
        )
    else:
        response = utlis.Response(
            error="The flight ID "
            + str(flight_id)
            + " you are trying to monitor doesn't exist."
        )
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.MONITOR,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# The check reservation feature
# Check the number of seat reserved for a specific Flight ID
def check_reservation(ip, flight_id):
    response = utlis.Response()
    error_code = 0

    if ip in reservation:
        if flight_id in reservation[ip]:
            seat = reservation[ip][flight_id]
            response = utlis.Response([utlis.CheckReservationResponse(seat)])
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID "
                + str(flight_id)
                + " was not found."
            )
            error_code = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flight_id) + " was not found."
        )
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.CHECK_RESERVATION,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# The cancellation feature
# Cancel the seat reservation of a specific Flight ID
def cancel_reservation(ip, flight_id):
    global df
    global reservation

    response = utlis.Response()
    error_code = 0

    if ip in reservation:
        if flight_id in reservation[ip]:
            seat = reservation[ip][flight_id]
            df.loc[df["FlightID"] == flight_id, "NumSeat"] += seat
            del reservation[ip][flight_id]
            send_updates(flight_id)
            response = utlis.Response(
                [
                    utlis.CancellationResponse(
                        "Seat reservation for Flight ID "
                        + str(flight_id)
                        + " is cancelled"
                    )
                ]
            )
        else:
            response = utlis.Response(
                error="Seat reservation for Flight ID "
                + str(flight_id)
                + " was not found."
            )
            error_code = 1
    else:
        response = utlis.Response(
            error="Seat reservation for Flight ID " + str(flight_id) + " was not found."
        )
        error_code = 1

    bytes_, size = utlis.marshal(
        response,
        utlis.ServiceType.CANCELLATION,
        utlis.MessageType.REPLY,
        error_code,
        0,
    )
    return bytes_, size


# function to pass the information to its respective services
def services(request, service_type, address, request_id):
    print("For Service:", Services[service_type])
    print("Request Parameters")

    if service_type == 0:
        source = request[0].source.lower()
        destination = request[0].destination.lower()
        print("Source:", source, "Destination:", destination)

        bytes_, size = search_flights(source, destination)
    elif service_type == 1:
        flight_id = request[0].flightId
        print("Flight ID:", flight_id)

        bytes_, size = get_flights_details(flight_id)
    elif service_type == 2:
        flight_id = request[0].flightId
        no_of_seats = request[0].noOfSeats

        print("Flight ID:", flight_id, "No. of seats:", no_of_seats)
        bytes_, size = reserve_seat(ip, flight_id, no_of_seats)
    elif service_type == 3:
        flight_id = request[0].flightId
        monitor_interval = request[0].monitorInterval

        print("Flight ID:", flight_id, "Monitor Interval:", monitor_interval)
        bytes_, size = monitor_flight(address, flight_id, request_id, monitor_interval)
    elif service_type == 4:
        flight_id = request[0].flightId

        print("Flight ID:", flight_id)
        bytes_, size = check_reservation(ip, flight_id)
    elif service_type == 5:
        flight_id = request[0].flightId

        print("Flight ID:", flight_id)
        bytes_, size = cancel_reservation(ip, flight_id)

    print("Updated Flights Information")
    print(tabulate(df, headers="keys", tablefmt="psql"))
    return bytes_, size


# function to decode the request byte and return the useful information
def decode_request(data):
    # Check if the bytearray is more than 41 in length
    # Because 23 Bytes for Request ID, 9 Bytes for Request Header, 4 Bytes Element Header, 5 Bytes Variable Header
    if len(data) > 41:
        request_id = data[:23]
        ip = utlis.decode_ip_from_request_id(request_id)
        try:
            socket.inet_aton(ip)
            request_byte = data[23:]
            request, service_type, _, packet_loss = utlis.unmarshal(request_byte)

            print("Received request from:", ip)
            print("Simulated packet loss:", bool(packet_loss))
            return request_id, ip, request, service_type, packet_loss
        except socket.error:
            return None, None, None, None, None
    else:
        return None, None, None, None, None


# Send response back to client
def send_response(address, request_id, bytes_, packet_loss):
    if not packet_loss:
        reply_bytes = bytearray()
        reply_bytes.extend(request_id)
        reply_bytes.extend(bytes_)
        s.sendto(reply_bytes, address)


# function for at most once operation
def at_most_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)

        request_id, ip, request, service_type, packet_loss = decode_request(data)
        if request_id == None:
            continue
        duplicated = check_duplicated_request_ids(request_id)
        print("Saved Request IDs:", requestIds)

        print("Duplicated Request:", bool(duplicated))
        if not duplicated:
            bytes_, size = services(request, service_type, address, request_id)

            set_response_cache(request_id, bytes_, 2 * 60)
            print("Saved Responses:", responseCache)
        else:
            bytes_ = get_response_cache(request_id)

        send_response(address, request_id, bytes_, packet_loss)


# function for at least once operation
def at_least_once():
    global s
    s = start_server()
    load_flight_info()

    while True:
        print("####### Server is listening #######")
        data, address = s.recvfrom(4096)

        request_id, ip, request, service_type, packet_loss = decode_request(data)
        if request_id == None:
            continue
        bytes_, size = services(request, service_type, address, request_id)
        send_response(address, request_id, bytes_, packet_loss)


# The main function
if __name__ == "__main__":
    # Get argument for at most once or at least once
    if len(sys.argv) == 2:
        choice = sys.argv[1]
    else:
        print("Run like : python3 main.py <choice[1: At Most Once, 2: At Least Once]>")
        exit(1)

    # Start at most once or at least once
    if choice == "1":
        start_cache_cleaner(60)  # Run every 60 seconds
        at_most_once()
    elif choice == "2":
        at_least_once()
    else:
        print("Run like : python3 main.py <choice[1: At Most Once, 2: At Least Once]>")
        exit(1)
