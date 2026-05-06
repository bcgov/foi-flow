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

// FileCopier copies a single S3 object from one location to another.
type FileCopier interface {
	CopyFile(ctx context.Context, srcBucket, srcKey, dstBucket, dstKey string) (int64, error)
}
