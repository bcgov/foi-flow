//go:build integration

package s3_test

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	awsconfig "github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	s3sdk "github.com/aws/aws-sdk-go-v2/service/s3"
	tc "github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"

	"publication-service/internal/config"
	pub "publication-service/internal/publish"
	pubs3 "publication-service/internal/storage/s3"
)

const (
	testAccessKey = "test-key"
	testSecretKey = "test-secret"
	testRegion    = "us-east-1"
)

type s3IntegrationHarness struct {
	raw    *s3sdk.Client
	client *pubs3.Client
}

func newS3IntegrationHarness(t *testing.T, ctx context.Context, buckets ...string) s3IntegrationHarness {
	t.Helper()

	req := tc.ContainerRequest{
		Image:        "chrislusf/seaweedfs:3.72",
		Cmd:          []string{"server", "-s3"},
		ExposedPorts: []string{"8333/tcp"},
		WaitingFor: wait.ForHTTP("/").
			WithPort("8333/tcp").
			WithStatusCodeMatcher(func(status int) bool { return status < 500 }).
			WithStartupTimeout(60 * time.Second),
	}
	container, err := tc.GenericContainer(ctx, tc.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		t.Fatalf("seaweedfs: %v", err)
	}
	t.Cleanup(func() { _ = container.Terminate(context.Background()) })

	host, err := container.Host(ctx)
	if err != nil {
		t.Fatalf("host: %v", err)
	}
	port, err := container.MappedPort(ctx, "8333/tcp")
	if err != nil {
		t.Fatalf("port: %v", err)
	}
	endpoint := fmt.Sprintf("http://%s:%s", host, port.Port())

	awsCfg, err := awsconfig.LoadDefaultConfig(ctx,
		awsconfig.WithRegion(testRegion),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			testAccessKey, testSecretKey, "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &endpoint
		o.UsePathStyle = true
	})

	for _, bucket := range buckets {
		_, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(bucket)})
		if err != nil {
			t.Fatalf("create bucket %q: %v", bucket, err)
		}
	}

	client, err := pubs3.NewClient(config.S3Config{
		Endpoint:        endpoint,
		Region:          testRegion,
		AccessKeyID:     testAccessKey,
		SecretAccessKey: testSecretKey,
		UsePathStyle:    true,
		RequestTimeout:  10 * time.Second,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	return s3IntegrationHarness{raw: raw, client: client}
}

func putS3Objects(t *testing.T, ctx context.Context, client *s3sdk.Client, bucket string, objects map[string]string) {
	t.Helper()

	for key, body := range objects {
		_, err := client.PutObject(ctx, &s3sdk.PutObjectInput{
			Bucket: aws.String(bucket),
			Key:    aws.String(key),
			Body:   bytes.NewReader([]byte(body)),
		})
		if err != nil {
			t.Fatalf("put %q: %v", key, err)
		}
	}
}

func TestClient_Copy_PreservesKeysAndSkipsFolderMarkers(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	h := newS3IntegrationHarness(t, ctx, "raw", "published")

	// Seed three real objects plus one folder-marker.
	objects := map[string]string{
		"src/a.txt":      "AAA",
		"src/b.txt":      "BBB",
		"src/deep/c.txt": "CCC",
	}
	putS3Objects(t, ctx, h.raw, "raw", objects)

	// Folder marker: zero-byte object whose key ends in "/".
	_, err := h.raw.PutObject(ctx, &s3sdk.PutObjectInput{
		Bucket: aws.String("raw"),
		Key:    aws.String("src/folder/"),
		Body:   bytes.NewReader(nil),
	})
	if err != nil {
		t.Fatalf("put folder marker: %v", err)
	}

	res, err := h.client.Copy(ctx,
		pub.S3Location{Bucket: "raw", Prefix: "src/"},
		pub.S3Location{Bucket: "published", Prefix: "dst/"},
	)
	if err != nil {
		t.Fatalf("Copy: %v", err)
	}
	if res.ObjectsCopied != 3 {
		t.Errorf("ObjectsCopied = %d, want 3", res.ObjectsCopied)
	}
	wantBytes := int64(len("AAA") + len("BBB") + len("CCC"))
	if res.BytesCopied != wantBytes {
		t.Errorf("BytesCopied = %d, want %d", res.BytesCopied, wantBytes)
	}

	// Assert each expected destination object exists with the right bytes.
	expected := map[string]string{
		"dst/a.txt":      "AAA",
		"dst/b.txt":      "BBB",
		"dst/deep/c.txt": "CCC",
	}
	for k, want := range expected {
		got, err := h.raw.GetObject(ctx, &s3sdk.GetObjectInput{
			Bucket: aws.String("published"),
			Key:    aws.String(k),
		})
		if err != nil {
			t.Fatalf("get %q: %v", k, err)
		}
		body, err := io.ReadAll(got.Body)
		_ = got.Body.Close()
		if err != nil {
			t.Fatalf("read %q: %v", k, err)
		}
		if string(body) != want {
			t.Errorf("%q body = %q, want %q", k, body, want)
		}
	}

	// Assert the folder-marker was NOT copied.
	_, err = h.raw.HeadObject(ctx, &s3sdk.HeadObjectInput{
		Bucket: aws.String("published"),
		Key:    aws.String("dst/folder/"),
	})
	if err == nil {
		t.Error("folder marker was copied; expected it to be skipped")
	}
}

func TestClient_Copy_EmptySourceIsNoOp(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	h := newS3IntegrationHarness(t, ctx, "raw", "published")

	res, err := h.client.Copy(ctx,
		pub.S3Location{Bucket: "raw", Prefix: "nothing/"},
		pub.S3Location{Bucket: "published", Prefix: "dst/"},
	)
	if err != nil {
		t.Fatalf("Copy: %v", err)
	}
	if res.ObjectsCopied != 0 || res.BytesCopied != 0 {
		t.Errorf("empty source should be no-op; got %+v", res)
	}
}

func TestClient_DeletePrefix_RemovesPackageObjects(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	const bucket = "dev-openinfopub"
	const prefix = "packages/PD-AGR-2026-047535/"
	h := newS3IntegrationHarness(t, ctx, bucket)

	objects := map[string]string{
		prefix + "openinfo/PD-AGR-2026-047535.html":     "html",
		prefix + "openinfo/document.pdf":                "pdf",
		prefix + "attachments/supporting.txt":           "supporting",
		"packages/PD-AGR-2026-OTHER/openinfo/keep.html": "keep",
	}
	putS3Objects(t, ctx, h.raw, bucket, objects)

	deleted, err := h.client.DeletePrefix(ctx, bucket, prefix)
	if err != nil {
		t.Fatalf("DeletePrefix: %v", err)
	}
	if deleted != 3 {
		t.Fatalf("DeletePrefix deleted %d objects, want 3", deleted)
	}

	list, err := h.raw.ListObjectsV2(ctx, &s3sdk.ListObjectsV2Input{
		Bucket: aws.String(bucket),
		Prefix: aws.String(prefix),
	})
	if err != nil {
		t.Fatalf("list deleted prefix: %v", err)
	}
	if len(list.Contents) != 0 {
		t.Fatalf("expected no objects under %q after DeletePrefix, found %d", prefix, len(list.Contents))
	}

	_, err = h.raw.HeadObject(ctx, &s3sdk.HeadObjectInput{
		Bucket: aws.String(bucket),
		Key:    aws.String("packages/PD-AGR-2026-OTHER/openinfo/keep.html"),
	})
	if err != nil {
		t.Fatalf("outside package object was removed: %v", err)
	}
}

func TestClient_Get(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	h := newS3IntegrationHarness(t, ctx, "published")

	if err := h.client.Upload(ctx, "published", "sitemap/sitemap_pages_1.xml", []byte("<xml/>"), "application/xml"); err != nil {
		t.Fatalf("Upload: %v", err)
	}
	got, err := h.client.Get(ctx, "published", "sitemap/sitemap_pages_1.xml")
	if err != nil {
		t.Fatalf("Get: %v", err)
	}
	if string(got) != "<xml/>" {
		t.Fatalf("Get body = %q", got)
	}
}
