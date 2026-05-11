//go:build integration

package messaging

import (
	"context"
	"encoding/json"
	"fmt"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"

	pub "publication-service/internal/publish"
	pg "publication-service/internal/storage/postgres"
)

func setupOutbox(t *testing.T) *OutboxRepo {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	c, err := tcpostgres.Run(ctx, "postgres:16-alpine",
		tcpostgres.WithDatabase("foi"),
		tcpostgres.WithUsername("foi"),
		tcpostgres.WithPassword("foi"),
		tcpostgres.BasicWaitStrategies(),
	)
	if err != nil {
		t.Fatalf("postgres: %v", err)
	}
	t.Cleanup(func() { _ = c.Terminate(context.Background()) })
	dsn, _ := c.ConnectionString(ctx, "sslmode=disable")
	if err := pg.Migrate(ctx, dsn); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)
	return NewOutboxRepo(pool)
}

func TestOutboxRepo_InsertAndClaim(t *testing.T) {
	repo := setupOutbox(t)
	ctx := context.Background()

	in := OutboxRow{
		EventID:   "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d91",
		EventType: "openinfo.publish.completed",
		TenantID:  "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		Envelope:  json.RawMessage(`{"event_id":"e"}`),
		Kind:      pub.KindOpenInfo,
	}
	if err := repo.Insert(ctx, in); err != nil {
		t.Fatalf("Insert: %v", err)
	}

	claimed, err := repo.ClaimBatch(ctx, 10)
	if err != nil {
		t.Fatalf("ClaimBatch: %v", err)
	}
	if len(claimed) != 1 {
		t.Fatalf("len(claimed) = %d", len(claimed))
	}

	if claimed[0].Kind != pub.KindOpenInfo {
		t.Errorf("Kind round-trip: got %q, want %q", claimed[0].Kind, pub.KindOpenInfo)
	}

	if err := repo.MarkPublished(ctx, claimed[0].ID, time.Now().UTC()); err != nil {
		t.Fatalf("MarkPublished: %v", err)
	}

	again, err := repo.ClaimBatch(ctx, 10)
	if err != nil {
		t.Fatalf("ClaimBatch second: %v", err)
	}
	if len(again) != 0 {
		t.Fatalf("expected 0 unpublished after MarkPublished, got %d", len(again))
	}
}

func TestOutboxRepo_KindRoundTrip_PD(t *testing.T) {
	repo := setupOutbox(t)
	ctx := context.Background()

	in := OutboxRow{
		EventID:   "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d92",
		EventType: "proactivedisclosure.publish.completed",
		TenantID:  "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		Envelope:  json.RawMessage(`{"event_id":"f"}`),
		Kind:      pub.KindProactiveDisclosure,
	}
	if err := repo.Insert(ctx, in); err != nil {
		t.Fatalf("Insert: %v", err)
	}

	claimed, err := repo.ClaimBatch(ctx, 10)
	if err != nil {
		t.Fatalf("ClaimBatch: %v", err)
	}
	if len(claimed) != 1 {
		t.Fatalf("len(claimed) = %d", len(claimed))
	}
	if claimed[0].Kind != pub.KindProactiveDisclosure {
		t.Errorf("Kind round-trip: got %q, want %q", claimed[0].Kind, pub.KindProactiveDisclosure)
	}
}

func TestOutboxRepo_ClaimBatch_NoDuplicates(t *testing.T) {
	repo := setupOutbox(t)
	ctx := context.Background()

	// Insert 5 rows.
	for i := 0; i < 5; i++ {
		err := repo.Insert(ctx, OutboxRow{
			EventID:   fmt.Sprintf("018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d%02d", i),
			EventType: "test.event",
			TenantID:  "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
			Envelope:  json.RawMessage(`{}`),
			Kind:      pub.KindOpenInfo,
		})
		if err != nil {
			t.Fatalf("Insert %d: %v", i, err)
		}
	}

	// Claim two batches of 3; they must not overlap.
	batch1, err := repo.ClaimBatch(ctx, 3)
	if err != nil {
		t.Fatalf("ClaimBatch 1: %v", err)
	}
	batch2, err := repo.ClaimBatch(ctx, 3)
	if err != nil {
		t.Fatalf("ClaimBatch 2: %v", err)
	}

	seen := map[int64]bool{}
	for _, r := range batch1 {
		seen[r.ID] = true
	}
	for _, r := range batch2 {
		if seen[r.ID] {
			t.Fatalf("row %d claimed by both batches", r.ID)
		}
	}

	if len(batch1) != 3 {
		t.Fatalf("batch1 len = %d, want 3", len(batch1))
	}
	if len(batch2) != 2 {
		t.Fatalf("batch2 len = %d, want 2", len(batch2))
	}
}

func TestOutboxRepo_BumpAttempts_ResetsClaim(t *testing.T) {
	repo := setupOutbox(t)
	ctx := context.Background()

	err := repo.Insert(ctx, OutboxRow{
		EventID:   "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d99",
		EventType: "test.event",
		TenantID:  "a7d9b2f1-4c3e-4e8b-9a21-1c2e8f7b9d10",
		Envelope:  json.RawMessage(`{}`),
		Kind:      pub.KindOpenInfo,
	})
	if err != nil {
		t.Fatalf("Insert: %v", err)
	}

	claimed, err := repo.ClaimBatch(ctx, 10)
	if err != nil {
		t.Fatalf("ClaimBatch: %v", err)
	}
	if len(claimed) != 1 {
		t.Fatalf("len(claimed) = %d", len(claimed))
	}

	// Bump (simulates publish failure) — should reset claimed_at.
	if err := repo.BumpAttempts(ctx, claimed[0].ID); err != nil {
		t.Fatalf("BumpAttempts: %v", err)
	}

	// Row should be immediately re-claimable.
	again, err := repo.ClaimBatch(ctx, 10)
	if err != nil {
		t.Fatalf("ClaimBatch after bump: %v", err)
	}
	if len(again) != 1 {
		t.Fatalf("expected 1 re-claimable row, got %d", len(again))
	}
}
