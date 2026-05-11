package messaging

import (
	"time"

	"publication-service/internal/config"
)

// TimeWindowGate controls whether the consumer should process events
// based on the current time of day and day of week.
// A nil gate is always open.
type TimeWindowGate struct {
	start    config.TimeOfDay
	end      config.TimeOfDay
	location *time.Location
	now      func() time.Time
}

// TimeWindowOption configures a TimeWindowGate.
type TimeWindowOption func(*TimeWindowGate)

// WithNowFunc overrides the clock for testing.
func WithNowFunc(fn func() time.Time) TimeWindowOption {
	return func(g *TimeWindowGate) { g.now = fn }
}

// NewTimeWindowGate creates a gate from the publish window configuration.
func NewTimeWindowGate(cfg config.PublishWindowConfig, opts ...TimeWindowOption) *TimeWindowGate {
	g := &TimeWindowGate{
		start:    cfg.Start,
		end:      cfg.End,
		location: cfg.Location,
		now:      time.Now,
	}
	for _, o := range opts {
		o(g)
	}
	return g
}

// IsOpen returns true if the current time is within the configured window
// on a weekday (Mon–Fri). A nil gate is always open.
func (g *TimeWindowGate) IsOpen() bool {
	if g == nil {
		return true
	}
	now := g.now().In(g.location)

	weekday := now.Weekday()
	if weekday == time.Saturday || weekday == time.Sunday {
		return false
	}

	current := config.TimeOfDay{Hour: now.Hour(), Minute: now.Minute()}
	// start <= current < end
	return !current.Before(g.start) && current.Before(g.end)
}
