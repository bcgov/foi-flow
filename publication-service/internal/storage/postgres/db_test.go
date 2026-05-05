package postgres

import (
	"context"
	"testing"
	"time"
)

func TestNewPool_RejectsBadDSN(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	if _, err := NewPool(ctx, "://not-a-dsn"); err == nil {
		t.Fatal("expected error for malformed DSN")
	}
}
