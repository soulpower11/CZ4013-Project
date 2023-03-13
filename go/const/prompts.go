package const_

import (
	"errors"
	"regexp"
	"strconv"
)

func GetTemplate() (string, string) {
	return `
	{{- if .ValidationError }} {{- Foreground "1" .Prompt }} {{ .Input -}}
	{{- else }} {{- Foreground "2" .Prompt }} {{ .Input -}}
	{{- end -}}
	`, `
	{{- print (Bold .Prompt) " " (Foreground "32"  (Mask .FinalValue)) "\n" -}}
	`
}

func GetCountryNameValidate() func(input string) error {
	countryNameValidate := func(input string) error {
		if len(input) < 1 {
			return errors.New("Country name cannot be empty")
		}
		reg, _ := regexp.Compile("^[^a-zA-Z]+$")
		if reg.MatchString(input) {
			return errors.New("Country name cannot only contain special characters or numbers")
		}
		return nil
	}
	return countryNameValidate
}

func GetFlightIdValidate() func(input string) error {
	flightIdValidate := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("Invalid Flight ID")
		}
		return nil
	}
	return flightIdValidate
}

func GetNoOfSeatsValidate() func(input string) error {
	noOfSeatsValidate := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("Invalid no. of seats")
		}
		return nil
	}
	return noOfSeatsValidate
}

func GetMonitorIntervalValidate() func(input string) error {
	monitorInterval := func(input string) error {
		_, err := strconv.ParseUint(input, 10, 32)
		if err != nil {
			return errors.New("Invalid interval")
		}
		return nil
	}
	return monitorInterval
}
