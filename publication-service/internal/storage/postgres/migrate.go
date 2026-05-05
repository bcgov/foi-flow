package postgres

import (
	"context"
	"embed"
	"fmt"
	"io/fs"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/jackc/pgx/v5/stdlib"
	"github.com/pressly/goose/v3"
	"github.com/pressly/goose/v3/lock"
)

//go:embed migrations/*.sql
var migrationFS embed.FS

// Migrate applies pending migrations, holding a Postgres advisory lock so
// multiple replicas starting simultaneously do not race.
func Migrate(ctx context.Context, dsn string) error {
	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		return fmt.Errorf("postgres.Migrate: pool: %w", err)
	}
	defer pool.Close()

	db := stdlib.OpenDBFromPool(pool)
	defer db.Close()

	migrationsSubFS, err := fs.Sub(migrationFS, "migrations")
	if err != nil {
		return fmt.Errorf("postgres.Migrate: sub fs: %w", err)
	}

	sessionLocker, err := lock.NewPostgresSessionLocker()
	if err != nil {
		return fmt.Errorf("postgres.Migrate: session locker: %w", err)
	}

	provider, err := goose.NewProvider(goose.DialectPostgres, db, migrationsSubFS,
		goose.WithSessionLocker(sessionLocker),
	)
	if err != nil {
		return fmt.Errorf("postgres.Migrate: provider: %w", err)
	}

	if _, err := provider.Up(ctx); err != nil {
		return fmt.Errorf("postgres.Migrate: up: %w", err)
	}

	return nil
}
