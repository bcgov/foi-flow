// Package messaging contains transport-neutral consumer, scheduler, and
// outbox-publisher loops, plus a broker abstraction with Redis Streams as
// its only current implementation.
package messaging

import (
	"context"
	"time"
)

// StreamMessage carries one delivered envelope plus the broker's ack handle.
type StreamMessage struct {
	ID      string // broker-assigned id (e.g. Redis stream entry id)
	Payload []byte // raw envelope JSON
}

// Broker abstracts at-least-once stream delivery.
type Broker interface {
	// EnsureGroup creates the consumer group if missing. Idempotent.
	EnsureGroup(ctx context.Context, stream, group string) error

	// Read blocks for up to timeout for the next message in (stream, group).
	// Returns (nil, nil) on timeout with no message — callers loop.
	Read(ctx context.Context, stream, group, consumer string, timeout time.Duration) (*StreamMessage, error)

	// Ack confirms a message id is processed.
	Ack(ctx context.Context, stream, group, id string) error

	// Publish appends an envelope to a stream with approximate MaxLen trim.
	Publish(ctx context.Context, stream string, payload []byte, maxLen int64) (string, error)

	// Trim runs an XTRIM MINID up to (but not including) the consumer group's
	// last-delivered id. Safe because Postgres is the source of truth.
	Trim(ctx context.Context, stream, group string) error

	// Close releases broker resources.
	Close() error
}
