package functions

import (
	"fmt"

	"github.com/jedib0t/go-pretty/text"
)

// TogglePacketLoss Toggle the simulated packet loss on and off
func TogglePacketLoss(packetLoss int32) int32 {
	if packetLoss == 0 {
		// Set packetLoss to 1 and print a message
		fmt.Printf("%s\n", text.FgGreen.Sprintf("%s", "Packet loss is turned on"))
		packetLoss = int32(1)
	} else {
		// Set packetLoss to 0 and print a message
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", "Packet loss is turned off"))
		packetLoss = int32(0)
	}
	return packetLoss
}
