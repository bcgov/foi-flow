//go:build integration

package postgres

import (
	"context"
	"testing"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func startPostgres(t *testing.T, ctx context.Context) string {
	t.Helper()
	container, err := tcpostgres.Run(ctx, "postgres:16-alpine",
		tcpostgres.WithDatabase("foi"),
		tcpostgres.WithUsername("foi"),
		tcpostgres.WithPassword("foi"),
		tcpostgres.BasicWaitStrategies(),
	)
	if err != nil {
		t.Fatalf("start postgres: %v", err)
	}
	t.Cleanup(func() { _ = container.Terminate(ctx) })
	dsn, err := container.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("conn string: %v", err)
	}
	return dsn
}

func TestMigrate_AppliesPlaceholderTwiceSafely(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	dsn := startPostgres(t, ctx)
	if err := Migrate(ctx, dsn); err != nil {
		t.Fatalf("first Migrate: %v", err)
	}
	if err := Migrate(ctx, dsn); err != nil {
		t.Fatalf("second Migrate (should be no-op): %v", err)
	}
}

func TestMigrate_WorkflowRequestSchema(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	dsn := startPostgres(t, ctx)
	if err := Migrate(ctx, dsn); err != nil {
		t.Fatalf("Migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)

	var count int
	err = pool.QueryRow(ctx,
		`SELECT count(*) FROM information_schema.tables WHERE table_name = 'workflow_request'`).Scan(&count)
	if err != nil {
		t.Fatalf("query: %v", err)
	}
	if count != 1 {
		t.Fatalf("workflow_request table not present (count=%d)", count)
	}

	err = pool.QueryRow(ctx,
		`SELECT count(*) FROM information_schema.columns
		 WHERE table_name = 'workflow_request' AND column_name = 'event_type'`).Scan(&count)
	if err != nil {
		t.Fatalf("query event_type column: %v", err)
	}
	if count != 1 {
		t.Fatal("workflow_request.event_type column not present")
	}
}

func TestMigrate_EventOutboxSchema(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	dsn := startPostgres(t, ctx)
	if err := Migrate(ctx, dsn); err != nil {
		t.Fatalf("Migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	t.Cleanup(pool.Close)

	var count int
	err = pool.QueryRow(ctx,
		`SELECT count(*) FROM information_schema.tables
         WHERE table_name = 'event_outbox'`).Scan(&count)
	if err != nil {
		t.Fatalf("query: %v", err)
	}
	if count != 1 {
		t.Fatalf("event_outbox table not present (count=%d)", count)
	}
}
