package utlis

import (
	"os"
	"time"

	"github.com/jedib0t/go-pretty/text"
	"github.com/jedib0t/go-pretty/v6/table"
	. "github.com/soulpower11/CZ4013-Project/const"
)

// DisplayFlightIds Display Flight IDs in a table
func DisplayFlightIds(flightIds []int32) {
	t := table.NewWriter()
	t.SetOutputMirror(os.Stdout)
	t.SetStyle(table.StyleColoredDark)
	t.AppendHeader(table.Row{"Flight ID"})

	for _, flightId := range flightIds {
		t.AppendRow([]interface{}{flightId})
	}

	t.Render()
}

// DisplayFlightInfo Display Flight Info in a table
func DisplayFlightInfo(flightInfos []QueryDepartureTimeResponse) {
	t := table.NewWriter()
	t.SetOutputMirror(os.Stdout)
	t.SetStyle(table.StyleColoredDark)
	t.AppendHeader(table.Row{"Departure Time", "Air Fare", "Seat Availability"})
	transformer := text.NewTimeTransformer(time.Kitchen, time.Local)
	for _, flightInfo := range flightInfos {
		t.AppendRow([]interface{}{transformer(flightInfo.DepartureTime), flightInfo.AirFare, flightInfo.SeatAvailability})
	}

	t.Render()
}
