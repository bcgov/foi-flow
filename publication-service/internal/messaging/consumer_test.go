package messaging

import (
	"context"
	"encoding/json"
	"errors"
	"sync"
	"testing"
	"time"

	"publication-service/internal/config"
	"publication-service/internal/events"
	pub "publication-service/internal/publish"
)

type fakeReadBroker struct {
	mu       sync.Mutex
	messages []*StreamMessage
	acked    []string
}

func (f *fakeReadBroker) EnsureGroup(_ context.Context, _, _ string) error { return nil }
func (f *fakeReadBroker) Trim(_ context.Context, _, _ string) error        { return nil }
func (f *fakeReadBroker) Close() error                                     { return nil }
func (f *fakeReadBroker) Publish(_ context.Context, _ string, _ []byte, _ int64) (string, error) {
	return "", nil
}

func (f *fakeReadBroker) Read(_ context.Context, _, _, _ string, _ time.Duration) (*StreamMessage, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if len(f.messages) == 0 {
		return nil, nil
	}
	m := f.messages[0]
	f.messages = f.messages[1:]
	return m, nil
}

func (f *fakeReadBroker) Ack(_ context.Context, _, _, id string) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.acked = append(f.acked, id)
	return nil
}

type failingReadBroker struct {
	mu          sync.Mutex
	ensureErr   error
	ensureErrs  int
	ensureCalls int
	readErr     error
	readCalls   int
	cancelAfter int
	cancel      context.CancelFunc
}

func (f *failingReadBroker) EnsureGroup(_ context.Context, _, _ string) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.ensureCalls++
	if f.ensureCalls <= f.ensureErrs {
		return f.ensureErr
	}
	return nil
}
func (f *failingReadBroker) Trim(_ context.Context, _, _ string) error { return nil }
func (f *failingReadBroker) Close() error                              { return nil }
func (f *failingReadBroker) Publish(_ context.Context, _ string, _ []byte, _ int64) (string, error) {
	return "", nil
}

func (f *failingReadBroker) Read(_ context.Context, _, _, _ string, _ time.Duration) (*StreamMessage, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.readCalls++
	if f.cancelAfter > 0 && f.readCalls >= f.cancelAfter && f.cancel != nil {
		f.cancel()
	}
	return nil, f.readErr
}

func (f *failingReadBroker) Ack(_ context.Context, _, _, _ string) error { return nil }

func (f *failingReadBroker) calls() int {
	f.mu.Lock()
	defer f.mu.Unlock()
	return f.readCalls
}

type fakeRepo struct {
	mu              sync.Mutex
	claimed         bool
	complete        bool
	retry           bool
	dead            bool
	bumpHash        string
	retryCount      int
	errorHashRepeat int
}

func (f *fakeRepo) Claim(_ context.Context, _ pub.ClaimRequest) (pub.ClaimResult, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.claimed {
		return pub.ClaimResult{Won: false}, nil
	}
	f.claimed = true
	return pub.ClaimResult{EventID: "e", Won: true}, nil
}

func (f *fakeRepo) MarkCompleted(_ context.Context, _ string, _ time.Time) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.complete = true
	return nil
}

func (f *fakeRepo) MarkRetry(_ context.Context, _, _, hash string, _ time.Time, maxRetries, poisonRepeatThreshold int) (pub.RetryResult, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	repeat := 1
	if f.bumpHash == hash {
		repeat = f.errorHashRepeat + 1
	}
	f.retryCount++
	f.errorHashRepeat = repeat
	f.bumpHash = hash
	if maxRetries > 0 && f.retryCount >= maxRetries {
		f.dead = true
		return pub.RetryResult{Dead: true}, nil
	}
	if poisonRepeatThreshold > 0 && repeat >= poisonRepeatThreshold {
		f.dead = true
		return pub.RetryResult{Dead: true}, nil
	}
	f.retry = true
	return pub.RetryResult{}, nil
}

func (f *fakeRepo) MarkDead(_ context.Context, _, _ string, _ pub.Class) error {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.dead = true
	return nil
}

type fakeOutbox struct{ inserted int }

func (f *fakeOutbox) Insert(_ context.Context, _ OutboxRow) error {
	f.inserted++
	return nil
}

// fakeNormalizer wraps a handler function and produces a fixed ClaimInfo + CompletionBuilder.
type fakeNormalizer struct {
	handlerErr error
}

func (f *fakeNormalizer) Normalize(env *events.Envelope) (ClaimInfo, HandlerFunc, CompletionBuilder, error) {
	info := ClaimInfo{
		EventID:       env.EventID,
		TenantID:      "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		CorrelationID: env.CorrelationID,
		Kind:          pub.KindOpenInfo,
	}
	handlerFn := func(ctx context.Context) error { return f.handlerErr }
	completionFn := func() (string, []byte, error) {
		id := "completion-id"
		b, _ := json.Marshal(map[string]string{"done": "true"})
		return id, b, nil
	}
	return info, handlerFn, completionFn, nil
}

// fakeValidator always passes unless configured to reject specific sources.
type fakeValidator struct{ rejectSource bool }

func (f *fakeValidator) Validate(env *events.Envelope) error {
	if f.rejectSource && env.Source == "rogue.service" {
		return pub.NewPermanent("source not allowed")
	}
	return nil
}

func sampleEnvelope(t *testing.T) []byte {
	t.Helper()
	env := events.Envelope{
		EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		EventType:     events.TypePublicationPublishRequested,
		Timestamp:     time.Now().UTC(),
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "req-1",
		Source:        "openinfo.enqueue.service",
		Payload:       json.RawMessage(`{"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10","axis_request_id":"HTH-2025-52023","source":{"bucket":"foi-raw","prefix":"incoming/a7d9b2f1/"},"destination":{"bucket":"foi-published","prefix":"out/a7d9b2f1/"}}`),
	}
	b, _ := json.Marshal(env)
	return b
}

func newConsumerForTest(broker Broker, repo PublishRepo, outbox OutboxInserter, normalizer EnvelopeNormalizer) *Consumer {
	v := &fakeValidator{}
	return NewConsumer(ConsumerConfig{
		Stream:                events.TypePublicationPublishRequested,
		CompletedStream:       events.TypePublicationPublishCompleted,
		CompletedEventType:    events.TypePublicationPublishCompleted,
		Kind:                  pub.KindOpenInfo,
		Group:                 "g",
		Consumer:              "c1",
		ReadTimeout:           50 * time.Millisecond,
		HandlerTimeout:        time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, broker, repo, outbox, normalizer, v)
}

func TestConsumer_HappyPath(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-1", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: nil}

	c := newConsumerForTest(broker, repo, outbox, normalizer)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.complete {
		t.Error("expected MarkCompleted")
	}
	if outbox.inserted != 1 {
		t.Errorf("outbox.inserted = %d", outbox.inserted)
	}
	if len(broker.acked) != 1 || broker.acked[0] != "redis-1" {
		t.Errorf("acked = %v", broker.acked)
	}
}

func TestConsumer_PermanentErrorGoesToDLQ(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-2", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: pub.NewPermanent("bad")}

	c := newConsumerForTest(broker, repo, outbox, normalizer)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.dead {
		t.Error("expected MarkDead on permanent error")
	}
	if outbox.inserted != 0 {
		t.Errorf("outbox should not be inserted, got %d", outbox.inserted)
	}
}

func TestConsumer_TransientErrorSchedulesRetry(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-3", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: pub.NewTransient("S3 5xx")}

	c := newConsumerForTest(broker, repo, outbox, normalizer)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.retry {
		t.Error("expected MarkRetry")
	}
	if repo.bumpHash == "" {
		t.Error("expected non-empty error hash")
	}
}

func TestConsumer_TransientErrorGoesDeadAfterMaxRetries(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-4", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{retryCount: 4}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: pub.NewTransient("S3 5xx")}

	c := newConsumerForTest(broker, repo, outbox, normalizer)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.dead {
		t.Error("expected transient error to go dead after max retries")
	}
	if repo.retry {
		t.Error("did not expect another retry after max retries")
	}
}

func TestConsumer_TransientErrorGoesDeadAfterPoisonRepeatThreshold(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-5", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{
		bumpHash:        pub.ErrorHash(pub.ClassTransient, "S3 5xx"),
		errorHashRepeat: 2,
	}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: pub.NewTransient("S3 5xx")}

	c := newConsumerForTest(broker, repo, outbox, normalizer)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.dead {
		t.Error("expected repeated transient error to go dead")
	}
	if repo.retry {
		t.Error("did not expect another retry after poison repeat threshold")
	}
}

func TestConsumer_RogueSourceIsDLQ(t *testing.T) {
	env := events.Envelope{
		EventID:       "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90",
		EventType:     events.TypePublicationPublishRequested,
		SchemaVersion: events.SchemaVersionV1,
		CorrelationID: "r",
		Source:        "rogue.service",
		Payload:       json.RawMessage(`{"tenant_id":"a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10","axis_request_id":"HTH-2025-52023","source":{"bucket":"foi-raw","prefix":"incoming/a7d9b2f1/"},"destination":{"bucket":"foi-published","prefix":"out/a7d9b2f1/"}}`),
	}
	b, _ := json.Marshal(env)
	broker := &fakeReadBroker{messages: []*StreamMessage{{ID: "x", Payload: b}}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: nil}

	v := &fakeValidator{rejectSource: true}
	c := NewConsumer(ConsumerConfig{
		Stream:                events.TypePublicationPublishRequested,
		CompletedStream:       events.TypePublicationPublishCompleted,
		CompletedEventType:    events.TypePublicationPublishCompleted,
		Kind:                  pub.KindOpenInfo,
		Group:                 "g",
		Consumer:              "c1",
		ReadTimeout:           50 * time.Millisecond,
		HandlerTimeout:        time.Second,
		MaxRetries:            5,
		PoisonRepeatThreshold: 3,
	}, broker, repo, outbox, normalizer, v)

	if err := c.Step(context.Background()); err != nil && !errors.Is(err, context.Canceled) {
		t.Fatalf("Step: %v", err)
	}
	if !repo.dead {
		t.Fatal("rogue source must be DLQed")
	}
}

func TestConsumer_RunBacksOffAfterReadErrors(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	broker := &failingReadBroker{
		readErr:     errors.New("redisstream.Read: dial tcp 10.98.16.18:6379: connect: connection refused"),
		cancelAfter: 3,
		cancel:      cancel,
	}
	c := newConsumerForTest(broker, &fakeRepo{}, &fakeOutbox{}, &fakeNormalizer{})
	c.cfg.ErrorBackoffMin = 20 * time.Millisecond
	c.cfg.ErrorBackoffMax = 20 * time.Millisecond

	start := time.Now()
	err := c.Run(ctx)
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("Run error = %v, want context.Canceled", err)
	}

	if got := broker.calls(); got != 3 {
		t.Fatalf("read calls = %d, want 3", got)
	}
	if elapsed := time.Since(start); elapsed < 40*time.Millisecond {
		t.Fatalf("Run retried without backoff; elapsed = %s", elapsed)
	}
}

func TestConsumer_RunRetriesEnsureGroupWithBackoff(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	broker := &failingReadBroker{
		ensureErr:   errors.New("redisstream.EnsureGroup: dial tcp 10.98.16.18:6379: connect: connection refused"),
		ensureErrs:  2,
		cancelAfter: 1,
		cancel:      cancel,
	}
	c := newConsumerForTest(broker, &fakeRepo{}, &fakeOutbox{}, &fakeNormalizer{})
	c.cfg.ErrorBackoffMin = 20 * time.Millisecond
	c.cfg.ErrorBackoffMax = 20 * time.Millisecond

	start := time.Now()
	err := c.Run(ctx)
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("Run error = %v, want context.Canceled", err)
	}

	if broker.ensureCalls != 3 {
		t.Fatalf("ensure calls = %d, want 3", broker.ensureCalls)
	}
	if elapsed := time.Since(start); elapsed < 40*time.Millisecond {
		t.Fatalf("Run retried EnsureGroup without backoff; elapsed = %s", elapsed)
	}
}

func TestConsumer_GateClosed_DiscardsMessage(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-gate-1", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: nil}

	closedGate := NewTimeWindowGate(config.PublishWindowConfig{
		Enabled:  true,
		Start:    config.TimeOfDay{Hour: 13, Minute: 0},
		End:      config.TimeOfDay{Hour: 15, Minute: 0},
		Location: time.UTC,
	}, WithNowFunc(func() time.Time {
		// 10:00 UTC on a Wednesday — outside 13:00–15:00
		return time.Date(2026, time.May, 6, 10, 0, 0, 0, time.UTC)
	}))

	c := newConsumerForTest(broker, repo, outbox, normalizer).WithTimeWindow(closedGate)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if repo.claimed {
		t.Error("repo should not have been claimed when gate is closed")
	}
	if repo.complete {
		t.Error("repo should not have been marked complete")
	}
	if outbox.inserted != 0 {
		t.Error("outbox should not have an entry")
	}
	if len(broker.acked) != 1 || broker.acked[0] != "redis-gate-1" {
		t.Errorf("message should be ACKed; acked = %v", broker.acked)
	}
}

func TestConsumer_GateOpen_ProcessesNormally(t *testing.T) {
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-gate-2", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: nil}

	openGate := NewTimeWindowGate(config.PublishWindowConfig{
		Enabled:  true,
		Start:    config.TimeOfDay{Hour: 13, Minute: 0},
		End:      config.TimeOfDay{Hour: 15, Minute: 0},
		Location: time.UTC,
	}, WithNowFunc(func() time.Time {
		// 14:00 UTC on a Wednesday — inside 13:00–15:00
		return time.Date(2026, time.May, 6, 14, 0, 0, 0, time.UTC)
	}))

	c := newConsumerForTest(broker, repo, outbox, normalizer).WithTimeWindow(openGate)
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.complete {
		t.Error("expected MarkCompleted when gate is open")
	}
	if outbox.inserted != 1 {
		t.Errorf("outbox.inserted = %d, want 1", outbox.inserted)
	}
}

func TestConsumer_NilGate_ProcessesNormally(t *testing.T) {
	// This is equivalent to the existing happy path — confirming nil gate doesn't break.
	broker := &fakeReadBroker{messages: []*StreamMessage{
		{ID: "redis-nil-gate", Payload: sampleEnvelope(t)},
	}}
	repo := &fakeRepo{}
	outbox := &fakeOutbox{}
	normalizer := &fakeNormalizer{handlerErr: nil}

	c := newConsumerForTest(broker, repo, outbox, normalizer) // no WithTimeWindow
	if err := c.Step(context.Background()); err != nil {
		t.Fatalf("Step: %v", err)
	}
	if !repo.complete {
		t.Error("expected MarkCompleted with nil gate")
	}
}
