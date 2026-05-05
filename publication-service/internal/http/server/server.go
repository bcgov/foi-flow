package server

import (
	"log/slog"
	"net/http"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

	"publication-service/internal/http/handlers"
	"publication-service/internal/observability"
)

type Options struct {
	Publications          http.Handler
	PublicationsUnpublish http.Handler
}

func New(addr string, logger *slog.Logger, build handlers.BuildInfo, opts Options) *http.Server {
	return &http.Server{
		Addr:              addr,
		Handler:           buildHandler(logger, build, opts),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
}

func buildHandler(logger *slog.Logger, build handlers.BuildInfo, opts Options) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/", handlers.Hello)
	mux.HandleFunc("/health", handlers.Health)
	mux.HandleFunc("/version", handlers.Version(build))
	if opts.Publications != nil {
		mux.Handle("/publications", opts.Publications)
	}
	if opts.PublicationsUnpublish != nil {
		mux.Handle("/publications/unpublish", opts.PublicationsUnpublish)
	}

	withObs := observability.Middleware(logger)(mux)

	// spanNameFormatter keeps span names static per route to avoid
	// high-cardinality names like `http.server /items/123`.
	return otelhttp.NewHandler(withObs, "http.server",
		otelhttp.WithFilter(shouldTraceHTTPRequest),
		otelhttp.WithSpanNameFormatter(spanName),
	)
}

func shouldTraceHTTPRequest(r *http.Request) bool {
	return r.URL.Path != "/health"
}

func spanName(_ string, r *http.Request) string {
	switch r.URL.Path {
	case "/":
		return "http.root.get"
	case "/health":
		return "http.health.get"
	case "/version":
		return "http.version.get"
	case "/publications":
		return "http.publications.post"
	case "/publications/unpublish":
		return "http.publications.unpublish.post"
	default:
		return "http.unknown"
	}
}
