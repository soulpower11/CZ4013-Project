package functions

import (
	"fmt"

	"github.com/jedib0t/go-pretty/text"
)

func TogglePacketLoss(packetLoss int32) int32 {
	if packetLoss == 0 {
		fmt.Printf("%s\n", text.FgGreen.Sprintf("%s", "Packet loss is turned on"))
		packetLoss = int32(1)
	} else {
		fmt.Printf("%s\n", text.FgRed.Sprintf("%s", "Packet loss is turned off"))
		packetLoss = int32(0)
	}
	return packetLoss
}
