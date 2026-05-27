package unpublish

import (
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"publication-service/internal/workflowresult"
)

type RequestRepo struct {
	*workflowresult.Repo[Result]
}

func NewRequestRepo(pool *pgxpool.Pool) *RequestRepo {
	completedAt := workflowresult.CompletedAt[Result]{
		Get: func(result *Result) time.Time { return result.CompletedAt },
		Set: func(result *Result, completedAt time.Time) { result.CompletedAt = completedAt },
	}
	return &RequestRepo{Repo: workflowresult.NewRepo[Result](pool, "unpublish.RequestRepo", completedAt)}
}
