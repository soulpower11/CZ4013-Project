package utlis

import (
	"os"

	"github.com/jedib0t/go-pretty/v6/table"
	. "github.com/soulpower11/CZ4031-Project/const"
)

func DisplayFlightIds(flightIds []int32) {
	t := table.NewWriter()
	t.SetOutputMirror(os.Stdout)
	t.SetStyle(table.StyleLight)
	t.AppendHeader(table.Row{"Flight ID"})

	for _, flightId := range flightIds {
		t.AppendRow([]interface{}{flightId})
	}

	t.Render()
}

func DisplaySeatsReserved(seatsReserved []int32) {
	t := table.NewWriter()
	t.SetOutputMirror(os.Stdout)
	t.SetStyle(table.StyleLight)
	t.AppendHeader(table.Row{"Seat Reserved"})

	for _, seatReserved := range seatsReserved {
		t.AppendRow([]interface{}{seatReserved})
	}

	t.Render()
}

func DisplayFlightInfo(flightInfos []QueryDepartureTimeResponse) {
	t := table.NewWriter()
	t.SetOutputMirror(os.Stdout)
	t.SetStyle(table.StyleLight)
	t.AppendHeader(table.Row{"Departure Time", "Air Fare", "Seat Availability"})

	for _, flightInfo := range flightInfos {
		t.AppendRow([]interface{}{flightInfo.DepartureTime, flightInfo.AirFare, flightInfo.SeatAvailability})
	}

	t.Render()
}
