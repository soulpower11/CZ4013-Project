package main

import (
	"fmt"

	functions "github.com/soulpower11/CZ4031-Project/func"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func main() {
	fmt.Println("----- Welcome to our airplane service -----")
	exit := false
	for !exit {
		options := []string{"Look for available flights", "Flight details", "Make seat reservation", "Monitor flight", "Check seat reservation", "Cancel seat reservation", "Exit"}
		choice := utlis.SelectPrompt("Please select your choice:", options)

		switch choice {
		case 0:
			functions.QueryFlightId()
			break
		case 1:
			functions.QueryDepartureTime()
			break
		case 2:
			functions.Reservation()
			break
		case 4:
			functions.CheckReservation()
			break
		case 5:
			functions.Cancellation()
			break
		case 6:
			exit = true
			break
		}
	}
}
