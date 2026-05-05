// Package events defines the standard event envelope shared by all producers
// and consumers in this service.
package events

import (
	"encoding/json"
	"fmt"
	"time"
)

// Envelope is the wire-level shape of every event published or consumed.
type Envelope struct {
	EventID       string          `json:"event_id"`
	EventType     string          `json:"event_type"`
	Timestamp     time.Time       `json:"timestamp"`
	SchemaVersion string          `json:"schema_version"`
	CorrelationID string          `json:"correlation_id"`
	Source        string          `json:"source"`
	Payload       json.RawMessage `json:"payload"`
	Meta          Meta            `json:"meta"`
}

// Meta holds system-level bookkeeping fields.
type Meta struct {
	RetryCount    int        `json:"retry_count"`
	FirstSeenAt   time.Time  `json:"first_seen_at"`
	LastAttemptAt *time.Time `json:"last_attempt_at,omitempty"`
	LastError     *string    `json:"last_error,omitempty"`
	Consumer      *string    `json:"consumer,omitempty"`
}

// UnmarshalEnvelope parses a JSON-encoded envelope.
func UnmarshalEnvelope(b []byte) (*Envelope, error) {
	var env Envelope
	if err := json.Unmarshal(b, &env); err != nil {
		return nil, fmt.Errorf("events: unmarshal envelope: %w", err)
	}
	return &env, nil
}
