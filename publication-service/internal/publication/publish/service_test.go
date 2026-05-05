package publish

import (
	"context"
	"io"
	"log/slog"
	"strings"
	"testing"

	pub "publication-service/internal/publish"
)

func discardLogger() *slog.Logger {
	return slog.New(slog.NewTextHandler(io.Discard, nil))
}

type fakeCopier struct {
	result pub.CopyResult
	err    error
}

func (f *fakeCopier) Copy(_ context.Context, _, _ pub.S3Location) (pub.CopyResult, error) {
	return f.result, f.err
}

type fakeUploader struct {
	uploaded map[string][]byte
	err      error
}

func (f *fakeUploader) Upload(_ context.Context, bucket, key string, body []byte, _ string) error {
	if f.uploaded == nil {
		f.uploaded = make(map[string][]byte)
	}
	f.uploaded[bucket+"/"+key] = body
	return f.err
}

func TestService_Handle_CopiesAndUploadsHTML(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 100}},
	}}
	uploader := &fakeUploader{}
	svc := NewService(copier, uploader, "https://public.example", discardLogger())

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-001",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
	}
	result, err := svc.Handle(context.Background(), d)
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if result.PublicationID != "HTH-001" {
		t.Errorf("PublicationID = %q", result.PublicationID)
	}
	if result.HTMLKey != "out/HTH-001.html" {
		t.Errorf("HTMLKey = %q", result.HTMLKey)
	}
	if !strings.Contains(result.PublicURL, "pub/out/HTH-001.html") {
		t.Errorf("PublicURL = %q", result.PublicURL)
	}
	if _, ok := uploader.uploaded["pub/out/HTH-001.html"]; !ok {
		t.Error("HTML not uploaded")
	}
}

func TestService_Handle_CopierError(t *testing.T) {
	copier := &fakeCopier{err: context.DeadlineExceeded}
	svc := NewService(copier, &fakeUploader{}, "https://x", discardLogger())

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		Source:      pub.S3Location{Bucket: "a", Prefix: "b/"},
		Destination: pub.S3Location{Bucket: "c", Prefix: "d/"},
	}
	_, err := svc.Handle(context.Background(), d)
	if err == nil {
		t.Fatal("expected error")
	}
}
