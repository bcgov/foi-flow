package messaging

import (
	"testing"
	"time"

	"publication-service/internal/config"
)

func gate(start, end config.TimeOfDay, tz string, now func() time.Time) *TimeWindowGate {
	loc, err := time.LoadLocation(tz)
	if err != nil {
		panic(err)
	}
	return NewTimeWindowGate(config.PublishWindowConfig{
		Enabled:  true,
		Start:    start,
		End:      end,
		Location: loc,
	}, WithNowFunc(now))
}

func fixedTime(year int, month time.Month, day, hour, min int, tz string) func() time.Time {
	loc, _ := time.LoadLocation(tz)
	return func() time.Time {
		return time.Date(year, month, day, hour, min, 0, 0, loc)
	}
}

func TestTimeWindowGate_OpenDuringWindow(t *testing.T) {
	// Wednesday 14:00 Vancouver — inside 13:00–15:00
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 6, 14, 0, "America/Vancouver"), // Wednesday
	)
	if !g.IsOpen() {
		t.Error("gate should be open at 14:00 on a Wednesday")
	}
}

func TestTimeWindowGate_ClosedBeforeWindow(t *testing.T) {
	// Wednesday 12:59 Vancouver — before 13:00
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 6, 12, 59, "America/Vancouver"),
	)
	if g.IsOpen() {
		t.Error("gate should be closed at 12:59")
	}
}

func TestTimeWindowGate_ClosedAfterWindow(t *testing.T) {
	// Wednesday 15:00 Vancouver — end is exclusive
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 6, 15, 0, "America/Vancouver"),
	)
	if g.IsOpen() {
		t.Error("gate should be closed at 15:00 (end is exclusive)")
	}
}

func TestTimeWindowGate_OpenAtExactStart(t *testing.T) {
	// Wednesday 13:00 — start is inclusive
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 6, 13, 0, "America/Vancouver"),
	)
	if !g.IsOpen() {
		t.Error("gate should be open at exactly 13:00 (inclusive)")
	}
}

func TestTimeWindowGate_ClosedOnSaturday(t *testing.T) {
	// Saturday 14:00 — weekday check fails
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 9, 14, 0, "America/Vancouver"), // Saturday
	)
	if g.IsOpen() {
		t.Error("gate should be closed on Saturday")
	}
}

func TestTimeWindowGate_ClosedOnSunday(t *testing.T) {
	// Sunday 14:00 — weekday check fails
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 10, 14, 0, "America/Vancouver"), // Sunday
	)
	if g.IsOpen() {
		t.Error("gate should be closed on Sunday")
	}
}

func TestTimeWindowGate_TimezoneConversion(t *testing.T) {
	// 21:00 UTC on Wednesday = 14:00 PDT (America/Vancouver, UTC-7)
	// Should be OPEN in Vancouver window 13:00–15:00
	g := gate(
		config.TimeOfDay{Hour: 13, Minute: 0},
		config.TimeOfDay{Hour: 15, Minute: 0},
		"America/Vancouver",
		fixedTime(2026, time.May, 6, 21, 0, "UTC"),
	)
	if !g.IsOpen() {
		t.Error("21:00 UTC is 14:00 PDT — gate should be open")
	}
}

func TestTimeWindowGate_NilGateIsAlwaysOpen(t *testing.T) {
	var g *TimeWindowGate
	if !g.IsOpen() {
		t.Error("nil gate should always be open")
	}
}
