package sitemapping

import (
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"publication-service/internal/workflowresult"
)

// RequestRepo stores sitemap-specific completion results in workflow_request.
type RequestRepo struct {
	*workflowresult.Repo[Result]
}

// NewRequestRepo constructs a RequestRepo around a pgxpool.
func NewRequestRepo(pool *pgxpool.Pool) *RequestRepo {
	return &RequestRepo{Repo: workflowresult.NewRepo[Result](
		pool,
		"sitemapping.RequestRepo",
		workflowresult.CompletedAt[Result]{Get: sitemapCompletedAt, Set: setSitemapCompletedAt},
	)}
}

func sitemapCompletedAt(result *Result) time.Time {
	return result.CompletedAt
}

func setSitemapCompletedAt(result *Result, completedAt time.Time) {
	result.CompletedAt = completedAt
}
