package observability

import (
	"context"
	"log/slog"
)

type (
	loggerCtxKey        struct{}
	correlationIDCtxKey struct{}
)

func WithLogger(ctx context.Context, l *slog.Logger) context.Context {
	return context.WithValue(ctx, loggerCtxKey{}, l)
}

func LoggerFrom(ctx context.Context) *slog.Logger {
	if l, ok := ctx.Value(loggerCtxKey{}).(*slog.Logger); ok {
		return l
	}
	return slog.Default()
}

func WithCorrelationID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, correlationIDCtxKey{}, id)
}

func CorrelationIDFrom(ctx context.Context) string {
	if v, ok := ctx.Value(correlationIDCtxKey{}).(string); ok {
		return v
	}
	return ""
}
