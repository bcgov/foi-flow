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

func TestClient_Copy_PreservesKeysAndSkipsFolderMarkers(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

	// Start SeaweedFS in S3 mode.
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

	// Raw SDK client for seeding and assertions.
	awsCfg, err := awsconfig.LoadDefaultConfig(ctx,
		awsconfig.WithRegion("us-east-1"),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			"test-key", "test-secret", "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &endpoint
		o.UsePathStyle = true
	})

	// Create source and destination buckets.
	for _, b := range []string{"raw", "published"} {
		_, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(b)})
		if err != nil {
			t.Fatalf("create bucket %q: %v", b, err)
		}
	}

	// Seed three real objects plus one folder-marker.
	objects := map[string]string{
		"src/a.txt":      "AAA",
		"src/b.txt":      "BBB",
		"src/deep/c.txt": "CCC",
	}
	for k, v := range objects {
		_, err := raw.PutObject(ctx, &s3sdk.PutObjectInput{
			Bucket: aws.String("raw"),
			Key:    aws.String(k),
			Body:   bytes.NewReader([]byte(v)),
		})
		if err != nil {
			t.Fatalf("put %q: %v", k, err)
		}
	}
	// Folder marker: zero-byte object whose key ends in "/".
	_, err = raw.PutObject(ctx, &s3sdk.PutObjectInput{
		Bucket: aws.String("raw"),
		Key:    aws.String("src/folder/"),
		Body:   bytes.NewReader(nil),
	})
	if err != nil {
		t.Fatalf("put folder marker: %v", err)
	}

	// Build the Client under test.
	client, err := pubs3.NewClient(config.S3Config{
		Endpoint:        endpoint,
		Region:          "us-east-1",
		AccessKeyID:     "test-key",
		SecretAccessKey: "test-secret",
		UsePathStyle:    true,
		RequestTimeout:  10 * time.Second,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	res, err := client.Copy(ctx,
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
		got, err := raw.GetObject(ctx, &s3sdk.GetObjectInput{
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
	_, err = raw.HeadObject(ctx, &s3sdk.HeadObjectInput{
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
		awsconfig.WithRegion("us-east-1"),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			"test-key", "test-secret", "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &endpoint
		o.UsePathStyle = true
	})
	for _, b := range []string{"raw", "published"} {
		_, err := raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String(b)})
		if err != nil {
			t.Fatalf("create bucket %q: %v", b, err)
		}
	}

	client, err := pubs3.NewClient(config.S3Config{
		Endpoint: endpoint, Region: "us-east-1",
		AccessKeyID: "test-key", SecretAccessKey: "test-secret",
		UsePathStyle: true, RequestTimeout: 10 * time.Second,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	res, err := client.Copy(ctx,
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

func TestClient_Get(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()

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
		awsconfig.WithRegion("us-east-1"),
		awsconfig.WithCredentialsProvider(credentials.NewStaticCredentialsProvider(
			"test-key", "test-secret", "")),
	)
	if err != nil {
		t.Fatalf("aws cfg: %v", err)
	}
	raw := s3sdk.NewFromConfig(awsCfg, func(o *s3sdk.Options) {
		o.BaseEndpoint = &endpoint
		o.UsePathStyle = true
	})
	_, err = raw.CreateBucket(ctx, &s3sdk.CreateBucketInput{Bucket: aws.String("published")})
	if err != nil {
		t.Fatalf("create bucket: %v", err)
	}

	client, err := pubs3.NewClient(config.S3Config{
		Endpoint: endpoint, Region: "us-east-1",
		AccessKeyID: "test-key", SecretAccessKey: "test-secret",
		UsePathStyle: true, RequestTimeout: 10 * time.Second,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}
	if err := client.Upload(ctx, "published", "sitemap/sitemap_pages_1.xml", []byte("<xml/>"), "application/xml"); err != nil {
		t.Fatalf("Upload: %v", err)
	}
	got, err := client.Get(ctx, "published", "sitemap/sitemap_pages_1.xml")
	if err != nil {
		t.Fatalf("Get: %v", err)
	}
	if string(got) != "<xml/>" {
		t.Fatalf("Get body = %q", got)
	}
}
