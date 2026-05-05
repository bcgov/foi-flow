package handlers

import (
	"fmt"
	"log/slog"
	"net/http"

	"publication-service/internal/observability"
)

func Hello(w http.ResponseWriter, r *http.Request) {
	log := observability.LoggerFrom(r.Context())

	if r.Method != http.MethodGet {
		http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
		return
	}

	if r.URL.Path != "/" {
		http.NotFound(w, r)
		return
	}

	log.InfoContext(r.Context(), "hello handled",
		slog.String("event_type", "hello.served"),
	)
	fmt.Fprintln(w, "Hello, World!")
}
