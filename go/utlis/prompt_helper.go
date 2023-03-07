package utlis

import (
	"github.com/manifoldco/promptui"
	. "github.com/soulpower11/CZ4031-Project/const"
)

func SelectPrompt(label string, items interface{}) int {
	prompt := promptui.Select{
		Label: label,
		Items: items,
	}

	choice, _, err := prompt.Run()

	if err != nil {
		return -1
	}

	return choice
}

func TextPrompt(label string, validate func(input string) error) *string {
	prompt := promptui.Prompt{
		Label:     label,
		Validate:  validate,
		Templates: GetTemplate(),
	}

	text, err := prompt.Run()

	for {
		if err == promptui.ErrInterrupt {
			return nil
		}
		if err == nil {
			break
		}
		text, err = prompt.Run()
	}

	return &text
}

func ConfirmPrompt(label string) *string {
	prompt := promptui.Prompt{
		Label:     label,
		IsConfirm: true,
	}

	result, err := prompt.Run()

	if err != nil {
		res := ""
		return &res
	}

	return &result
}
