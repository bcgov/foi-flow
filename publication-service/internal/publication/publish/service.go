package publish

import (
	"context"
	"fmt"
	"log/slog"
	"strings"
	"time"

	"publication-service/internal/htmlindex"
	pub "publication-service/internal/publish"
)

// Option configures the Service.
type Option func(*Service)

// WithFileCopier sets the FileCopier used to copy additional files.
func WithFileCopier(fc pub.FileCopier) Option {
	return func(s *Service) {
		s.fileCopier = fc
	}
}

// Service handles publication.publish.requested events for all kinds.
type Service struct {
	copier     pub.Copier
	uploader   pub.Uploader
	fileCopier pub.FileCopier
	publicURL  string
	log        *slog.Logger
}

// NewService constructs a handler backed by the given Copier, Uploader, and public S3 base URL.
func NewService(c pub.Copier, u pub.Uploader, publicURL string, log *slog.Logger, opts ...Option) *Service {
	svc := &Service{copier: c, uploader: u, publicURL: publicURL, log: log}
	for _, opt := range opts {
		opt(svc)
	}
	return svc
}

// Handle copies source files, renders the HTML index, uploads it, and returns publication metadata.
func (s *Service) Handle(ctx context.Context, d *Domain) (pub.PublishResult, error) {
	res, err := s.copier.Copy(ctx, d.Source, d.Destination)
	if err != nil {
		return pub.PublishResult{}, err
	}

	// Copy additional files to destination.
	if s.fileCopier != nil {
		for _, af := range d.AdditionalFiles {
			srcBucket, srcKey, parseErr := parseS3URI(af.S3URI)
			if parseErr != nil {
				return pub.PublishResult{}, parseErr
			}
			dstKey := d.Destination.Prefix + af.Filename
			size, copyErr := s.fileCopier.CopyFile(ctx, srcBucket, srcKey, d.Destination.Bucket, dstKey)
			if copyErr != nil {
				return pub.PublishResult{}, fmt.Errorf("publish: copy additional file %q: %w", af.Filename, copyErr)
			}
			res.Objects = append(res.Objects, pub.CopiedObject{Key: af.Filename, Size: size})
			res.ObjectsCopied++
			res.BytesCopied += size
		}
	}

	vars := buildTemplateVars(d, res, s.publicURL, time.Now().UTC())
	html, err := htmlindex.Render(vars)
	if err != nil {
		return pub.PublishResult{}, fmt.Errorf("publish: render HTML index: %w", err)
	}

	htmlKey := d.Destination.Prefix + d.RequestID + ".html"
	if err := s.uploader.Upload(ctx, d.Destination.Bucket, htmlKey, html, "text/html; charset=utf-8"); err != nil {
		return pub.PublishResult{}, err
	}

	logAttrs := []any{
		"kind", string(d.Kind),
		"event_id", d.EventID,
		"correlation_id", d.CorrelationID,
		"tenant_id", d.TenantID,
		"src_bucket", d.Source.Bucket,
		"src_prefix", d.Source.Prefix,
		"dst_bucket", d.Destination.Bucket,
		"dst_prefix", d.Destination.Prefix,
		"objects_copied", res.ObjectsCopied,
		"bytes_copied", res.BytesCopied,
		"html_key", htmlKey,
	}
	if d.Kind == pub.KindProactiveDisclosure {
		logAttrs = append(logAttrs, "category", d.Category, "report_period", d.ReportPeriod)
	}
	if len(d.AdditionalFiles) > 0 {
		logAttrs = append(logAttrs, "additional_files_copied", len(d.AdditionalFiles))
	}
	s.log.InfoContext(ctx, "artifact publish succeeded", logAttrs...)

	return pub.PublishResult{
		PublicationID: d.RequestID,
		HTMLKey:       htmlKey,
		PublicURL:     strings.TrimRight(s.publicURL, "/") + "/" + d.Destination.Bucket + "/" + htmlKey,
	}, nil
}
