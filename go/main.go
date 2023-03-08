package main

import (
	"fmt"

	functions "github.com/soulpower11/CZ4031-Project/func"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func main() {
	fmt.Println("----- Welcome to our airplane service -----")
	exit := false
	timeOut := int32(0)

	for !exit {
		options := []string{"Look for available flights", "Flight details", "Make seat reservation", "Monitor flight", "Check seat reservation", "Cancel seat reservation", "Toggle Simulated Timeout", "Exit"}
		choice := utlis.SelectPrompt("Please select your choice:", options)

		switch choice {
		case 0:
			functions.QueryFlightId(timeOut)
			break
		case 1:
			functions.QueryDepartureTime(timeOut)
			break
		case 2:
			functions.Reservation(timeOut)
			break
		case 3:
			functions.MonitorFlight(timeOut)
			break
		case 4:
			functions.CheckReservation(timeOut)
			break
		case 5:
			functions.Cancellation(timeOut)
			break
		case 6:
			if timeOut == 0 {
				println("Time Out is turned on")
				timeOut = int32(1)
			} else {
				println("Time Out is turned off")
				timeOut = int32(0)
			}
			break
		case 7:
			exit = true
			break
		}
	}
}
