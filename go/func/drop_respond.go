package functions

import (
	"github.com/soulpower11/CZ4031-Project/utlis"
)

func Drop_respond() (on int) {
	on = 0
	options := []string{"0", "1"}
	choice := utlis.SelectPrompt("Please select your choice:", options)

	switch choice {
	case 0:
		on = 0

	case 1:
		on = 1
	}
	return on
}
