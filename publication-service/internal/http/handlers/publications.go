package handlers

import (
	"bytes"
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

// utf8BOM is the byte-order mark sometimes prepended by Windows tools.
var utf8BOM = []byte{0xEF, 0xBB, 0xBF}

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
			log.WarnContext(r.Context(), "publish request body read failed",
				slog.String("event_type", "publications.bad_request"),
				slog.Any("error", err),
			)
			http.Error(w, "request body could not be read: "+err.Error(), http.StatusBadRequest)
			return
		}
		body = bytes.TrimPrefix(body, utf8BOM)
		if !json.Valid(body) {
			log.WarnContext(r.Context(), "publish request body is not valid JSON",
				slog.String("event_type", "publications.bad_request"),
				slog.String("body", string(body)),
			)
			http.Error(w, "request body is not valid JSON", http.StatusBadRequest)
			return
		}

		resp, err := orchestrator.Publish(r.Context(), body)
		if err != nil {
			if publishnow.IsClientError(err) {
				log.WarnContext(r.Context(), "publish request client error",
					slog.String("event_type", "publications.bad_request"),
					slog.String("body", string(body)),
					slog.Any("error", err),
				)
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
			log.WarnContext(r.Context(), "unpublish request body read failed",
				slog.String("event_type", "publications.bad_request"),
				slog.Any("error", err),
			)
			http.Error(w, "request body could not be read: "+err.Error(), http.StatusBadRequest)
			return
		}
		body = bytes.TrimPrefix(body, utf8BOM)
		if !json.Valid(body) {
			log.WarnContext(r.Context(), "unpublish request body is not valid JSON",
				slog.String("event_type", "publications.bad_request"),
				slog.String("body", string(body)),
			)
			http.Error(w, "request body is not valid JSON", http.StatusBadRequest)
			return
		}

		resp, err := orchestrator.Unpublish(r.Context(), body)
		if err != nil {
			if unpublishnow.IsClientError(err) {
				log.WarnContext(r.Context(), "unpublish request client error",
					slog.String("event_type", "publications.bad_request"),
					slog.String("body", string(body)),
					slog.Any("error", err),
				)
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
