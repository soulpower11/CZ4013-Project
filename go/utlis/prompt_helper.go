package utlis

import (
	"github.com/erikgeiser/promptkit"
	"github.com/erikgeiser/promptkit/selection"
	"github.com/erikgeiser/promptkit/textinput"
	. "github.com/soulpower11/CZ4031-Project/const"
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
	prompt := selection.New(label, items)
	prompt.PageSize = 5
	prompt.Filter = nil
	prompt.ResultTemplate = GetSelectTemplate()

	choice, err := prompt.RunPrompt()
	if err != nil {
		return -1
	}

	return indexOf(items, choice)
}

func TextPrompt(label string, validate func(input string) error) *string {
	prompt := textinput.New(label)
	prompt.Validate = validate
	template, resultTemplate := GetTextTemplate()
	prompt.Template = template
	prompt.ResultTemplate = resultTemplate

	text, err := prompt.RunPrompt()

	for {
		if err == promptkit.ErrAborted {
			return nil
		}
		if err == nil {
			break
		}
		text, err = prompt.RunPrompt()
	}

	return &text
}
