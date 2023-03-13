package utlis

import (
	"github.com/erikgeiser/promptkit/selection"
	"github.com/erikgeiser/promptkit/textinput"
	"github.com/manifoldco/promptui"
	// . "github.com/soulpower11/CZ4031-Project/const"
)

func indexOf(arr []string, val string) int {
	for pos, v := range arr {
		if v == val {
			return pos
		}
	}
	return -1
}

func SelectPrompt(label string, items []string) int {
	sp := selection.New(label, items)

	// sp.PageSize = 3

	choice, err := sp.RunPrompt()
	if err != nil {
		return -1
	}

	return indexOf(items, choice)
}

func TextPrompt(label string, validate func(input string) error) *string {
	prompt := textinput.New(label)
	prompt.Validate = validate

	// prompt := promptui.Prompt{
	// 	Label:     label,
	// 	Validate:  validate,
	// 	Templates: GetTemplate(),
	// }

	text, err := prompt.RunPrompt()

	for {
		if err == promptui.ErrInterrupt {
			return nil
		}
		if err == nil {
			break
		}
		text, err = prompt.RunPrompt()
	}

	return &text
}
