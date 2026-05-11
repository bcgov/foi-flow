package handlers

import (
	"encoding/json"
	"log/slog"
	"net/http"

	"publication-service/internal/observability"
)

func Health(w http.ResponseWriter, r *http.Request) {
	log := observability.LoggerFrom(r.Context())

	if r.Method != http.MethodGet {
		http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	response := struct {
		Status string `json:"status"`
	}{
		Status: "ok",
	}

	if err := json.NewEncoder(w).Encode(response); err != nil {
		log.ErrorContext(r.Context(), "encode health response failed",
			slog.String("event_type", "health.encode_failed"),
			slog.Any("error", err),
		)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
	}
}
