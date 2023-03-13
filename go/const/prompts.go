package const_

import (
	"errors"
	"regexp"
	"strconv"
)

// GetSelectTemplate Get the template of the selection prompt
func GetSelectTemplate() string {
	return `
	{{- print (Foreground "2" "v") " " (Final .FinalChoice) "\n" -}}
	`
}

// GetTextTemplate Get the template of the text prompt
func GetTextTemplate() (string, string) {
	return `
	{{- if .ValidationError }} {{- Foreground "1" .Prompt }} {{ .Input -}}
	{{- else }} {{- Foreground "2" .Prompt }} {{ .Input -}}
	{{- end -}}
	{{- if .ValidationError -}}
	{{- (print (Foreground "1" "\n>> ") (Foreground "1" .ValidationError.Error)) -}}
	{{- end -}}
	`, `
	{{- print (Bold .Prompt) " " (Foreground "32"  (Mask .FinalValue)) "\n" -}}
	`
}

// GetCountryNameValidate Get the validation function for Country Name
func GetCountryNameValidate() func(input string) error {
	countryNameValidate := func(input string) error {
		if len(input) < 1 {
			return errors.New("country name cannot be empty")
		}
		reg, _ := regexp.Compile("^[a-zA-Z]+$")
		if !reg.MatchString(input) {
			return errors.New("country name cannot only contain special characters or numbers")
		}
		return nil
	}
	return countryNameValidate
}

// GetFlightIdValidate Get the validation function for Flight ID
func GetFlightIdValidate() func(input string) error {
	flightIdValidate := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("invalid Flight ID")
		}
		return nil
	}
	return flightIdValidate
}

// GetNoOfSeatsValidate Get the validation function for No. of Seats
func GetNoOfSeatsValidate() func(input string) error {
	noOfSeatsValidate := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("invalid no. of seats")
		}
		return nil
	}
	return noOfSeatsValidate
}

// GetMonitorIntervalValidate Get the validation function for Monitor Interval
func GetMonitorIntervalValidate() func(input string) error {
	monitorInterval := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("invalid interval")
		}
		return nil
	}
	return monitorInterval
}
