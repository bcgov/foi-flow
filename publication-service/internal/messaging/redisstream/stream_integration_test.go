//go:build integration

package redisstream

import (
	"context"
	"strings"
	"testing"
	"time"

	tcredis "github.com/testcontainers/testcontainers-go/modules/redis"
)

func startRedis(t *testing.T) string {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	c, err := tcredis.Run(ctx, "redis:7-alpine")
	if err != nil {
		t.Fatalf("start redis: %v", err)
	}
	t.Cleanup(func() { _ = c.Terminate(context.Background()) })
	// ConnectionString returns "redis://host:port" — strip the scheme for go-redis Addr.
	connStr, err := c.ConnectionString(ctx)
	if err != nil {
		t.Fatalf("connection string: %v", err)
	}
	addr := strings.TrimPrefix(connStr, "redis://")
	return addr
}

func TestBroker_PublishReadAck(t *testing.T) {
	addr := startRedis(t)
	b, err := New(Options{Addr: addr})
	if err != nil {
		t.Fatalf("New: %v", err)
	}
	t.Cleanup(func() { _ = b.Close() })

	ctx := context.Background()
	if err := b.EnsureGroup(ctx, "s", "g"); err != nil {
		t.Fatalf("EnsureGroup: %v", err)
	}
	if err := b.EnsureGroup(ctx, "s", "g"); err != nil {
		t.Fatalf("EnsureGroup idempotent: %v", err)
	}

	id, err := b.Publish(ctx, "s", []byte(`{"hello":"world"}`), 100)
	if err != nil {
		t.Fatalf("Publish: %v", err)
	}
	if id == "" {
		t.Fatal("Publish returned empty id")
	}

	msg, err := b.Read(ctx, "s", "g", "c1", 2*time.Second)
	if err != nil {
		t.Fatalf("Read: %v", err)
	}
	if msg == nil || string(msg.Payload) != `{"hello":"world"}` {
		t.Fatalf("Read payload = %v", msg)
	}

	if err := b.Ack(ctx, "s", "g", msg.ID); err != nil {
		t.Fatalf("Ack: %v", err)
	}

	gone, err := b.Read(ctx, "s", "g", "c1", 500*time.Millisecond)
	if err != nil {
		t.Fatalf("Read post-ack: %v", err)
	}
	if gone != nil {
		t.Fatalf("expected nil after ack, got %v", gone)
	}
}
