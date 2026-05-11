package observability

import (
	"log/slog"
	"net/http"

	"github.com/google/uuid"
)

const (
	headerCorrelationID = "X-Correlation-ID"
	headerRequestID     = "X-Request-ID"
	headerTenantID      = "X-Tenant-ID"
)

// Middleware attaches correlation/request/tenant IDs and a request-scoped
// logger to the request context. It must run inside the otelhttp handler so
// the active span is already on the context.
func Middleware(base *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			correlationID := r.Header.Get(headerCorrelationID)
			if correlationID == "" {
				correlationID = uuid.NewString()
			}
			requestID := r.Header.Get(headerRequestID)
			if requestID == "" {
				requestID = "req-" + uuid.NewString()
			}

			attrs := []any{
				slog.String("request_id", requestID),
			}
			if tenantID := r.Header.Get(headerTenantID); tenantID != "" {
				attrs = append(attrs, slog.String("tenant_id", tenantID))
			}
			reqLogger := base.With(attrs...)

			ctx := r.Context()
			ctx = WithCorrelationID(ctx, correlationID)
			ctx = WithLogger(ctx, reqLogger)

			w.Header().Set(headerCorrelationID, correlationID)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}
