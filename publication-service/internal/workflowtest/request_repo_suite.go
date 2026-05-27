//go:build integration

package workflowtest

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"

	pub "publication-service/internal/publish"
	pg "publication-service/internal/storage/postgres"
)

type RequestRepo[R comparable] interface {
	FindCompleted(ctx context.Context, kind pub.Kind, tenantID string, correlationID string) (R, bool, error)
	MarkSucceeded(ctx context.Context, eventID string, result R) error
}

type RequestRepoSuite[R comparable] struct {
	NewRepo      func(*pgxpool.Pool) RequestRepo[R]
	ClaimRequest func(eventID string, correlationID string) pub.ClaimRequest
	SampleResult func() R
	Kind         pub.Kind
	OtherKind    pub.Kind
	TenantID     string
}

func RunRequestRepoSuite[R comparable](t *testing.T, suite RequestRepoSuite[R]) {
	t.Helper()
	t.Run("FindCompletedFalseBeforeSuccess", func(t *testing.T) {
		repo, pubRepo, _ := setupRequestRepo(t, suite.NewRepo)
		claimRequest(t, pubRepo, suite.ClaimRequest(testEventID, "corr-1"))

		_, ok, err := repo.FindCompleted(context.Background(), suite.Kind, suite.TenantID, "corr-1")
		if err != nil {
			t.Fatalf("FindCompleted: %v", err)
		}
		if ok {
			t.Fatal("FindCompleted returned true before success")
		}
	})

	t.Run("MarkSucceededStoresFullResult", func(t *testing.T) {
		repo, pubRepo, pool := setupRequestRepo(t, suite.NewRepo)
		claimRequest(t, pubRepo, suite.ClaimRequest(testEventID, "corr-1"))
		result := suite.SampleResult()

		if err := repo.MarkSucceeded(context.Background(), testEventID, result); err != nil {
			t.Fatalf("MarkSucceeded: %v", err)
		}

		var state string
		var raw []byte
		if err := pool.QueryRow(context.Background(),
			`SELECT state, result FROM workflow_request WHERE event_id=$1`, testEventID,
		).Scan(&state, &raw); err != nil {
			t.Fatalf("query stored result: %v", err)
		}
		if state != "completed" {
			t.Fatalf("state = %q, want completed", state)
		}
		var stored R
		if err := json.Unmarshal(raw, &stored); err != nil {
			t.Fatalf("unmarshal stored result: %v", err)
		}
		if stored != result {
			t.Fatalf("stored result mismatch:\n got: %#v\nwant: %#v", stored, result)
		}
	})

	t.Run("FindCompletedReturnsStoredResultByKindTenantAndCorrelationID", func(t *testing.T) {
		repo, pubRepo, _ := setupRequestRepo(t, suite.NewRepo)
		claimRequest(t, pubRepo, suite.ClaimRequest(testEventID, "corr-1"))
		want := suite.SampleResult()
		if err := repo.MarkSucceeded(context.Background(), testEventID, want); err != nil {
			t.Fatalf("MarkSucceeded: %v", err)
		}

		got, ok, err := repo.FindCompleted(context.Background(), suite.Kind, suite.TenantID, "corr-1")
		if err != nil {
			t.Fatalf("FindCompleted: %v", err)
		}
		if !ok {
			t.Fatal("FindCompleted returned false after success")
		}
		if got != want {
			t.Fatalf("FindCompleted result mismatch:\n got: %#v\nwant: %#v", got, want)
		}
	})

	t.Run("FindCompletedDoesNotMatchDifferentCorrelationID", func(t *testing.T) {
		repo, pubRepo, _ := setupRequestRepo(t, suite.NewRepo)
		claimRequest(t, pubRepo, suite.ClaimRequest(testEventID, "corr-original"))
		if err := repo.MarkSucceeded(context.Background(), testEventID, suite.SampleResult()); err != nil {
			t.Fatalf("MarkSucceeded: %v", err)
		}

		_, ok, err := repo.FindCompleted(context.Background(), suite.Kind, suite.TenantID, "corr-new")
		if err != nil {
			t.Fatalf("FindCompleted: %v", err)
		}
		if ok {
			t.Fatal("FindCompleted returned true for a different correlation ID")
		}
	})

	t.Run("FindCompletedDoesNotMatchDifferentKind", func(t *testing.T) {
		repo, pubRepo, _ := setupRequestRepo(t, suite.NewRepo)
		claimRequest(t, pubRepo, suite.ClaimRequest(testEventID, "corr-1"))
		if err := repo.MarkSucceeded(context.Background(), testEventID, suite.SampleResult()); err != nil {
			t.Fatalf("MarkSucceeded: %v", err)
		}

		_, ok, err := repo.FindCompleted(context.Background(), suite.OtherKind, suite.TenantID, "corr-1")
		if err != nil {
			t.Fatalf("FindCompleted: %v", err)
		}
		if ok {
			t.Fatal("FindCompleted returned true for a different kind")
		}
	})
}

const testEventID = "018f2e7a-1c6b-7c0a-9f8d-3e4a2b1c5d90"

func setupRequestRepo[R comparable](
	t *testing.T,
	newRepo func(*pgxpool.Pool) RequestRepo[R],
) (RequestRepo[R], *pub.Repo, *pgxpool.Pool) {
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
	dsn, err := c.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("connection string: %v", err)
	}
	if err := pg.Migrate(ctx, dsn); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)
	return newRepo(pool), pub.NewRepo(pool), pool
}

func claimRequest(t *testing.T, repo *pub.Repo, req pub.ClaimRequest) {
	t.Helper()
	if req.Now.IsZero() {
		req.Now = time.Now().UTC()
	}
	if _, err := repo.Claim(context.Background(), req); err != nil {
		t.Fatalf("Claim: %v", err)
	}
}
