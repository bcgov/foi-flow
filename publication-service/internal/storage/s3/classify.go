// Package s3 is the ArtifactPublisher's thin wrapper over AWS SDK v2 for
// S3-compatible object storage. It exposes one operation — Copy — and
// translates SDK errors into publish.TransientError / publish.PermanentError
// so the consumer loop's retry/DLQ machinery can act on them.
package s3

import (
	"context"
	"errors"
	"net"

	smithy "github.com/aws/smithy-go"

	"publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

// classifyS3Error maps a raw SDK error into a publish.* classified error.
// Fail-safe default: unknown errors are transient (retried), never permanent (DLQ'd).
func classifyS3Error(err error) error {
	if err == nil {
		return nil
	}

	// Context errors → transient. The consumer may cancel on shutdown; we want
	// the event to come back around rather than land in DLQ.
	if errors.Is(err, context.DeadlineExceeded) || errors.Is(err, context.Canceled) {
		return publish.NewTransient(err.Error())
	}

	// net.Error timeouts → transient.
	var netErr net.Error
	if errors.As(err, &netErr) && netErr.Timeout() {
		return publish.NewTransient(err.Error())
	}

	// Known S3 API errors with a permanent class.
	var api smithy.APIError
	if errors.As(err, &api) {
		switch api.ErrorCode() {
		case "NoSuchKey", "NotFound":
			return sitemapping.ErrObjectNotFound
		case "NoSuchBucket",
			"AccessDenied",
			"InvalidAccessKeyId",
			"SignatureDoesNotMatch":
			return publish.NewPermanent(api.ErrorCode() + ": " + api.ErrorMessage())
		}
		// Other SDK API errors fall through to transient.
		return publish.NewTransient(api.ErrorCode() + ": " + api.ErrorMessage())
	}

	// Fail-safe: unknown → transient.
	return publish.NewTransient(err.Error())
}
