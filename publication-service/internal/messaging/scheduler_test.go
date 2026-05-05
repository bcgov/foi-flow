package messaging

import (
	"context"
	"encoding/json"
	"sync"
	"testing"
	"time"

	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

type fakeSchedulerRepo struct {
	mu     sync.Mutex
	due    []pub.DueRow
	stuck  int64
	dueErr error
}

func (r *fakeSchedulerRepo) ClaimDue(_ context.Context, limit int, _ time.Time) ([]pub.DueRow, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.dueErr != nil {
		return nil, r.dueErr
	}
	if limit > len(r.due) {
		limit = len(r.due)
	}
	out := r.due[:limit:limit]
	r.due = r.due[limit:]
	return append([]pub.DueRow(nil), out...), nil
}

func (r *fakeSchedulerRepo) ResetStuck(_ context.Context, _ time.Time) (int64, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.stuck, nil
}

type fakePublisher struct {
	mu        sync.Mutex
	published [][]byte
}

func (p *fakePublisher) EnsureGroup(_ context.Context, _, _ string) error { return nil }
func (p *fakePublisher) Read(_ context.Context, _, _, _ string, _ time.Duration) (*StreamMessage, error) {
	return nil, nil
}
func (p *fakePublisher) Ack(_ context.Context, _, _, _ string) error { return nil }
func (p *fakePublisher) Trim(_ context.Context, _, _ string) error   { return nil }
func (p *fakePublisher) Close() error                                { return nil }
func (p *fakePublisher) Publish(_ context.Context, _ string, payload []byte, _ int64) (string, error) {
	p.mu.Lock()
	defer p.mu.Unlock()
	p.published = append(p.published, payload)
	return "1-0", nil
}

func TestScheduler_ReenqueuesDueRowsReusingEventID(t *testing.T) {
	repo := &fakeSchedulerRepo{
		due: []pub.DueRow{{
			EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
			TenantID:      "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
			CorrelationID: "req-1",
			SchemaVersion: events.SchemaVersionV1,
			Payload:       json.RawMessage(`{"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10"}`),
			RetryCount:    1,
		}},
	}
	broker := &fakePublisher{}
	s := NewScheduler(SchedulerConfig{
		PublishStream: events.TypePublicationPublishRequested,
		PublishSource: "publication.publish.service",
		BatchSize:     10,
		StreamMaxLen:  100,
	}, repo, broker)
	if err := s.Tick(context.Background()); err != nil {
		t.Fatalf("Tick: %v", err)
	}
	if len(broker.published) != 1 {
		t.Fatalf("published = %d", len(broker.published))
	}
	var env events.Envelope
	if err := json.Unmarshal(broker.published[0], &env); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}
	if env.EventID != "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90" {
		t.Errorf("EventID changed on re-enqueue: %q", env.EventID)
	}
	if env.Meta.RetryCount != 1 {
		t.Errorf("Meta.RetryCount = %d", env.Meta.RetryCount)
	}
}

type fakeBrokerWithStreams struct {
	mu      sync.Mutex
	records []struct{ stream, eventID string }
}

func (f *fakeBrokerWithStreams) EnsureGroup(_ context.Context, _, _ string) error { return nil }
func (f *fakeBrokerWithStreams) Read(_ context.Context, _, _, _ string, _ time.Duration) (*StreamMessage, error) {
	return nil, nil
}
func (f *fakeBrokerWithStreams) Ack(_ context.Context, _, _, _ string) error { return nil }
func (f *fakeBrokerWithStreams) Trim(_ context.Context, _, _ string) error   { return nil }
func (f *fakeBrokerWithStreams) Close() error                                { return nil }
func (f *fakeBrokerWithStreams) Publish(_ context.Context, stream string, payload []byte, _ int64) (string, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	var env events.Envelope
	_ = json.Unmarshal(payload, &env)
	f.records = append(f.records, struct{ stream, eventID string }{stream, env.EventID})
	return "1-0", nil
}
func (f *fakeBrokerWithStreams) streamOf(eventID string) string {
	f.mu.Lock()
	defer f.mu.Unlock()
	for _, r := range f.records {
		if r.eventID == eventID {
			return r.stream
		}
	}
	return ""
}

func TestScheduler_RoutesByKind(t *testing.T) {
	repo := &fakeSchedulerRepo{due: []pub.DueRow{
		{EventID: "oi-1", Payload: json.RawMessage(`{}`), Kind: pub.KindOpenInfo},
		{EventID: "pd-1", Payload: json.RawMessage(`{}`), Kind: pub.KindProactiveDisclosure},
	}}
	broker := &fakeBrokerWithStreams{}
	s := NewScheduler(SchedulerConfig{
		PublishStream: "publication.publish.requested",
		PublishSource: "publication.publish.service",
		BatchSize:     10,
		Interval:      time.Second,
	}, repo, broker)
	if err := s.Tick(context.Background()); err != nil {
		t.Fatalf("Tick: %v", err)
	}
	if broker.streamOf("oi-1") != "publication.publish.requested" {
		t.Errorf("oi-1 routed to %q", broker.streamOf("oi-1"))
	}
	if broker.streamOf("pd-1") != "publication.publish.requested" {
		t.Errorf("pd-1 routed to %q", broker.streamOf("pd-1"))
	}
}

func TestScheduler_RoutesSitemapKinds(t *testing.T) {
	repo := &fakeSchedulerRepo{due: []pub.DueRow{
		{
			EventID:   "oi-map-1",
			EventType: events.TypePublicationSitemappingRequested,
			Payload:   json.RawMessage(`{}`),
			Kind:      pub.KindOpenInfoSitemap,
		},
		{
			EventID:   "pd-map-1",
			EventType: events.TypePublicationSitemappingRequested,
			Payload:   json.RawMessage(`{}`),
			Kind:      pub.KindProactiveDisclosureSitemap,
		},
	}}
	broker := &fakeBrokerWithStreams{}
	s := NewScheduler(SchedulerConfig{
		SitemapStream: "publication.sitemapping.requested",
		SitemapSource: "publication.sitemapping.service",
		BatchSize:     10,
		Interval:      time.Second,
	}, repo, broker)
	if err := s.Tick(context.Background()); err != nil {
		t.Fatalf("Tick: %v", err)
	}
	if broker.streamOf("oi-map-1") != "publication.sitemapping.requested" {
		t.Errorf("oi-map-1 routed to %q", broker.streamOf("oi-map-1"))
	}
	if broker.streamOf("pd-map-1") != "publication.sitemapping.requested" {
		t.Errorf("pd-map-1 routed to %q", broker.streamOf("pd-map-1"))
	}
}
