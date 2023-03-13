package main

import (
	"fmt"

	. "github.com/jedib0t/go-pretty/text"
	functions "github.com/soulpower11/CZ4031-Project/func"
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func main() {
	fmt.Printf("%s\n", FgWhite.Sprintf("%s", FormatTitle.Apply("----- Welcome to our airplane service -----")))
	exit := false
	packetLoss := int32(0)

	for !exit {
		options := []string{"Look for available flights", "Get flight details", "Make seat reservation", "Monitor flight", "Check seat reservation", "Cancel seat reservation", "Toggle Simulated Packet Loss", "Exit"}
		choice := utlis.SelectPrompt("Use the arrow keys to navigate: ↓ ↑ → ←\nPlease select your choice:", options)

		switch choice {
		case 0:
			functions.QueryFlightId(packetLoss)
			break
		case 1:
			functions.QueryDepartureTime(packetLoss)
			break
		case 2:
			functions.Reservation(packetLoss)
			break
		case 3:
			functions.MonitorFlight(packetLoss)
			break
		case 4:
			functions.CheckReservation(packetLoss)
			break
		case 5:
			functions.Cancellation(packetLoss)
			break
		case 6:
			packetLoss = functions.TogglePacketLoss(packetLoss)
			break
		case 7:
			exit = true
			break
		}
	}
}
