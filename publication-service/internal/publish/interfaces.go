package publish

import "context"

// Copier copies every real object under src to dst, preserving relative keys.
type Copier interface {
	Copy(ctx context.Context, src, dst S3Location) (CopyResult, error)
}

// Uploader writes a file to an S3 bucket.
type Uploader interface {
	Upload(ctx context.Context, bucket, key string, body []byte, contentType string) error
}
