package utlis

import (
	"github.com/erikgeiser/promptkit"
	"github.com/erikgeiser/promptkit/selection"
	"github.com/erikgeiser/promptkit/textinput"
	. "github.com/soulpower11/CZ4013-Project/const"
)

// SelectPrompt helper function for a select prompt
func SelectPrompt(label string, items []string) int {
	prompt := selection.New(label, items)
	prompt.PageSize = 5
	prompt.Filter = nil
	prompt.ResultTemplate = GetSelectTemplate()

	choice, err := prompt.RunPrompt()
	if err != nil {
		return -1
	}

	return IndexOfStringArr(items, choice)
}

// TextPrompt helper function for a text prompt
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
