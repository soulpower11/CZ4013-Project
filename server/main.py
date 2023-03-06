import socket
import sys
import utlis
import csv

ip = "127.0.0.1"
port = 8080

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
