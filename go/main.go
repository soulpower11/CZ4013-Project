package main

import (
	"fmt"

	functions "github.com/soulpower11/CZ4031-Project/func"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

var on int = 0

func main() {
	fmt.Println("----- Welcome to our airplane service -----")
	exit := false
	for !exit {
		options := []string{"Look for available flights", "Flight details", "Make seat reservation", "Monitor flight", "Check seat reservation", "Cancel seat reservation", "Toggle simulation", "Exit"}
		choice := utlis.SelectPrompt("Please select your choice", options)

		switch choice {
		case 0:
			functions.QueryFlightId(on)
			break
		case 1:
			functions.QueryDepartureTime(on)
			break
		case 2:
			functions.Reservation(on)
			break
		case 3:
			functions.MonitorFlight(on)
			break
		case 4:
			functions.CheckReservation(on)
			break
		case 5:
			functions.Cancellation(on)
			break
		case 6:
			on = functions.Drop_respond()
		case 7:
			exit = true
			break
		}
	}
}
