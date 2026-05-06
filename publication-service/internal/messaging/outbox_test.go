package messaging

import (
	"context"
	"encoding/json"
	"errors"
	"sync"
	"testing"
	"time"
)

type fakeBroker struct {
	mu        sync.Mutex
	published [][]byte
	failNext  bool
}

func (f *fakeBroker) EnsureGroup(_ context.Context, _, _ string) error { return nil }
func (f *fakeBroker) Read(_ context.Context, _, _, _ string, _ time.Duration) (*StreamMessage, error) {
	return nil, nil
}
func (f *fakeBroker) Ack(_ context.Context, _, _, _ string) error { return nil }
func (f *fakeBroker) Trim(_ context.Context, _, _ string) error   { return nil }
func (f *fakeBroker) Close() error                                { return nil }
func (f *fakeBroker) Publish(_ context.Context, _ string, payload []byte, _ int64) (string, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.failNext {
		f.failNext = false
		return "", errors.New("simulated XADD failure")
	}
	f.published = append(f.published, payload)
	return "1-0", nil
}

type fakeOutboxStore struct {
	rows      []OutboxRow
	published map[int64]bool
	bumped    map[int64]int
	mu        sync.Mutex
}

func (s *fakeOutboxStore) ClaimBatch(_ context.Context, limit int) ([]OutboxRow, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if limit > len(s.rows) {
		limit = len(s.rows)
	}
	out := s.rows[:limit:limit]
	s.rows = s.rows[limit:]
	return append([]OutboxRow(nil), out...), nil
}

func (s *fakeOutboxStore) MarkPublished(_ context.Context, id int64, _ time.Time) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.published == nil {
		s.published = map[int64]bool{}
	}
	s.published[id] = true
	return nil
}

func (s *fakeOutboxStore) BumpAttempts(_ context.Context, id int64) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.bumped == nil {
		s.bumped = map[int64]int{}
	}
	s.bumped[id]++
	return nil
}

func TestOutbox_DrainsBatchToBroker(t *testing.T) {
	store := &fakeOutboxStore{rows: []OutboxRow{
		{ID: 1, EventType: "x", Envelope: json.RawMessage(`{"a":1}`)},
		{ID: 2, EventType: "x", Envelope: json.RawMessage(`{"a":2}`)},
	}}
	broker := &fakeBroker{}
	pub := NewOutboxPublisher(store, broker, 100)
	if err := pub.Drain(context.Background()); err != nil {
		t.Fatalf("Drain: %v", err)
	}
	if len(broker.published) != 2 {
		t.Fatalf("published count = %d", len(broker.published))
	}
	if !store.published[1] || !store.published[2] {
		t.Fatalf("published map = %v", store.published)
	}
}

func TestOutbox_BumpsOnPublishFailure(t *testing.T) {
	store := &fakeOutboxStore{rows: []OutboxRow{
		{ID: 7, EventType: "x", Envelope: json.RawMessage(`{}`)},
	}}
	broker := &fakeBroker{failNext: true}
	pub := NewOutboxPublisher(store, broker, 100)
	if err := pub.Drain(context.Background()); err != nil {
		t.Fatalf("Drain: %v", err)
	}
	if store.bumped[7] != 1 {
		t.Fatalf("bumped = %v", store.bumped)
	}
	if store.published[7] {
		t.Fatal("must not mark published on failure")
	}
}
