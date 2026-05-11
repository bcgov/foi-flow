package s3

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"net/url"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	awsconfig "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	s3sdk "github.com/aws/aws-sdk-go-v2/service/s3"
	s3types "github.com/aws/aws-sdk-go-v2/service/s3/types"

	"publication-service/internal/config"
	"publication-service/internal/publish"
)

// Client is a thin wrapper over the AWS SDK v2 S3 client, scoped to the
// single Copy operation the ArtifactPublisher needs.
type Client struct {
	api     *s3sdk.Client
	timeout time.Duration
}

// NewClient constructs a Client from the service's S3 config.
// Validates the endpoint is an absolute URL with scheme and host.
func NewClient(cfg config.S3Config) (*Client, error) {
	u, err := url.Parse(cfg.Endpoint)
	if err != nil || u.Scheme == "" || u.Host == "" {
		return nil, fmt.Errorf("s3: endpoint %q must be an absolute URL (e.g. http://host:port)", cfg.Endpoint)
	}

	awsCfg, err := awsconfig.LoadDefaultConfig(context.Background(),
		awsconfig.WithRegion(cfg.Region),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			cfg.AccessKeyID, cfg.SecretAccessKey, "")),
	)
	if err != nil {
		return nil, fmt.Errorf("s3: load aws config: %w", err)
	}

	api := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &cfg.Endpoint
		o.UsePathStyle = cfg.UsePathStyle
	})

	timeout := cfg.RequestTimeout
	if timeout <= 0 {
		timeout = 30 * time.Second
	}
	return &Client{api: api, timeout: timeout}, nil
}

// Copy lists every real object under src and copies it to dst, preserving
// the relative key suffix. Folder-marker objects (keys ending in "/") are
// skipped. Overwrites on destination collisions. Empty source is a
// successful no-op returning CopyResult{0, 0}.
//
// Both prefixes MUST already be canonical (empty, or ending in "/"), as
// guaranteed by publish.Normalize.
func (c *Client) Copy(ctx context.Context, src, dst publish.S3Location) (publish.CopyResult, error) {
	var res publish.CopyResult

	if err := ctx.Err(); err != nil {
		return res, classifyS3Error(err)
	}

	paginator := s3sdk.NewListObjectsV2Paginator(c.api, &s3sdk.ListObjectsV2Input{
		Bucket: &src.Bucket,
		Prefix: &src.Prefix,
	})

	for paginator.HasMorePages() {
		pageCtx, cancel := context.WithTimeout(ctx, c.timeout)
		page, err := paginator.NextPage(pageCtx)
		cancel()
		if err != nil {
			return res, classifyS3Error(err)
		}

		for _, obj := range page.Contents {
			if obj.Key == nil {
				continue
			}
			key := *obj.Key
			// Skip folder-marker zero-byte objects.
			if strings.HasSuffix(key, "/") {
				continue
			}

			rel := strings.TrimPrefix(key, src.Prefix)
			destKey := dst.Prefix + rel
			copySource := src.Bucket + "/" + url.PathEscape(key)

			copyInput := &s3sdk.CopyObjectInput{
				Bucket:     &dst.Bucket,
				Key:        &destKey,
				CopySource: &copySource,
			}
			if acl := publicReadACLForBucket(dst.Bucket); acl != nil {
				copyInput.ACL = *acl
			}

			copyCtx, copyCancel := context.WithTimeout(ctx, c.timeout)
			_, err := c.api.CopyObject(copyCtx, copyInput)
			copyCancel()
			if err != nil {
				return res, classifyS3Error(err)
			}
			var sizeVal int64
			if obj.Size != nil {
				sizeVal = *obj.Size
			}
			res.Objects = append(res.Objects, publish.CopiedObject{Key: rel, Size: sizeVal})
			res.ObjectsCopied++
			res.BytesCopied += sizeVal
		}
	}

	return res, nil
}

// Upload writes body to bucket/key with the given content-type.
func (c *Client) Upload(ctx context.Context, bucket, key string, body []byte, contentType string) error {
	uploadCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()
	putInput := &s3sdk.PutObjectInput{
		Bucket:      &bucket,
		Key:         &key,
		Body:        bytes.NewReader(body),
		ContentType: &contentType,
	}
	if acl := publicReadACLForBucket(bucket); acl != nil {
		putInput.ACL = *acl
	}

	_, err := c.api.PutObject(uploadCtx, putInput)
	if err != nil {
		return classifyS3Error(err)
	}
	return nil
}

func publicReadACLForBucket(bucket string) *s3types.ObjectCannedACL {
	switch bucket {
	case "dev-openinfopub", "openinfopub":
		acl := s3types.ObjectCannedACLPublicRead
		return &acl
	default:
		return nil
	}
}

// Get reads bucket/key into memory.
func (c *Client) Get(ctx context.Context, bucket, key string) ([]byte, error) {
	getCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()
	out, err := c.api.GetObject(getCtx, &s3sdk.GetObjectInput{
		Bucket: &bucket,
		Key:    &key,
	})
	if err != nil {
		return nil, classifyS3Error(err)
	}
	defer out.Body.Close()
	body, err := io.ReadAll(out.Body)
	if err != nil {
		return nil, publish.NewTransient(err.Error())
	}
	return body, nil
}

// Delete removes one object. Missing objects are treated as successful
// deletes because S3 DeleteObject is idempotent.
func (c *Client) Delete(ctx context.Context, bucket, key string) error {
	deleteCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()
	_, err := c.api.DeleteObject(deleteCtx, &s3sdk.DeleteObjectInput{
		Bucket: &bucket,
		Key:    &key,
	})
	if err != nil {
		return classifyS3Error(err)
	}
	return nil
}

// CopyFile copies a single object from srcBucket/srcKey to dstBucket/dstKey.
// Returns the size of the copied object.
func (c *Client) CopyFile(ctx context.Context, srcBucket, srcKey, dstBucket, dstKey string) (int64, error) {
	copyCtx, cancel := context.WithTimeout(ctx, c.timeout)
	defer cancel()

	copySource := srcBucket + "/" + url.PathEscape(srcKey)
	copyInput := &s3sdk.CopyObjectInput{
		Bucket:     &dstBucket,
		Key:        &dstKey,
		CopySource: &copySource,
	}
	if acl := publicReadACLForBucket(dstBucket); acl != nil {
		copyInput.ACL = *acl
	}

	resp, err := c.api.CopyObject(copyCtx, copyInput)
	if err != nil {
		return 0, classifyS3Error(err)
	}

	// CopyObject doesn't return size directly; use HeadObject.
	headCtx, headCancel := context.WithTimeout(ctx, c.timeout)
	defer headCancel()
	head, err := c.api.HeadObject(headCtx, &s3sdk.HeadObjectInput{
		Bucket: &dstBucket,
		Key:    &dstKey,
	})
	if err != nil {
		// Copy succeeded but head failed — return 0 size, not an error.
		_ = resp
		return 0, nil
	}
	if head.ContentLength != nil {
		return *head.ContentLength, nil
	}
	return 0, nil
}

// DeletePrefix deletes every real object under prefix. Folder marker objects
// are skipped to match Copy's behavior.
func (c *Client) DeletePrefix(ctx context.Context, bucket, prefix string) (int, error) {
	if strings.TrimSpace(prefix) == "" {
		return 0, publish.NewPermanent("s3: delete prefix must not be empty")
	}
	if err := ctx.Err(); err != nil {
		return 0, classifyS3Error(err)
	}

	paginator := s3sdk.NewListObjectsV2Paginator(c.api, &s3sdk.ListObjectsV2Input{
		Bucket: &bucket,
		Prefix: &prefix,
	})

	deleted := 0
	for paginator.HasMorePages() {
		pageCtx, cancel := context.WithTimeout(ctx, c.timeout)
		page, err := paginator.NextPage(pageCtx)
		cancel()
		if err != nil {
			return deleted, classifyS3Error(err)
		}
		if len(page.Contents) == 0 {
			continue
		}

		objects := make([]s3types.ObjectIdentifier, 0, len(page.Contents))
		for _, obj := range page.Contents {
			if obj.Key == nil || strings.HasSuffix(*obj.Key, "/") {
				continue
			}
			key := *obj.Key
			objects = append(objects, s3types.ObjectIdentifier{Key: &key})
		}
		if len(objects) == 0 {
			continue
		}

		deleteCtx, deleteCancel := context.WithTimeout(ctx, c.timeout)
		_, err = c.api.DeleteObjects(deleteCtx, &s3sdk.DeleteObjectsInput{
			Bucket: &bucket,
			Delete: &s3types.Delete{Objects: objects, Quiet: aws.Bool(true)},
		})
		deleteCancel()
		if err != nil {
			return deleted, classifyS3Error(err)
		}
		deleted += len(objects)
	}
	return deleted, nil
}
