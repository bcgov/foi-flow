package handlers

import (
	"context"
	"encoding/json"
	"io"
	"log/slog"
	"net/http"

	"publication-service/internal/observability"
	"publication-service/internal/publishnow"
	"publication-service/internal/unpublishnow"
)

const maxPublicationsBodyBytes = 1 << 20

type PublicationsOrchestrator interface {
	Publish(context.Context, []byte) (publishnow.Response, error)
}

type PublicationsUnpublishOrchestrator interface {
	Unpublish(context.Context, []byte) (unpublishnow.Response, error)
}

func Publications(orchestrator PublicationsOrchestrator) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log := observability.LoggerFrom(r.Context())
		if r.Method != http.MethodPost {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, maxPublicationsBodyBytes))
		if err != nil {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}
		if !json.Valid(body) {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		resp, err := orchestrator.Publish(r.Context(), body)
		if err != nil {
			if publishnow.IsClientError(err) {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			log.ErrorContext(r.Context(), "publication request failed",
				slog.String("event_type", "publications.publish_failed"),
				slog.Any("error", err),
			)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(resp); err != nil {
			log.ErrorContext(r.Context(), "encode publication response failed",
				slog.String("event_type", "publications.encode_failed"),
				slog.Any("error", err),
			)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		}
	})
}

func PublicationsUnpublish(orchestrator PublicationsUnpublishOrchestrator) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		log := observability.LoggerFrom(r.Context())
		if r.Method != http.MethodPost {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}

		body, err := io.ReadAll(http.MaxBytesReader(w, r.Body, maxPublicationsBodyBytes))
		if err != nil {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}
		if !json.Valid(body) {
			http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
			return
		}

		resp, err := orchestrator.Unpublish(r.Context(), body)
		if err != nil {
			if unpublishnow.IsClientError(err) {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			log.ErrorContext(r.Context(), "publication unpublish request failed",
				slog.String("event_type", "publications.unpublish_failed"),
				slog.Any("error", err),
			)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(resp); err != nil {
			log.ErrorContext(r.Context(), "encode publication unpublish response failed",
				slog.String("event_type", "publications.unpublish_encode_failed"),
				slog.Any("error", err),
			)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		}
	})
}
