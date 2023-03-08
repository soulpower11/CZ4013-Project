package functions

import (
	"fmt"
)

func TogglePacketLoss(packetLoss int32) int32 {
	if packetLoss == 0 {
		fmt.Println("Packet loss is turned on")
		packetLoss = int32(1)
	} else {
		fmt.Println("Packet loss is turned off")
		packetLoss = int32(0)
	}
	return packetLoss
}
