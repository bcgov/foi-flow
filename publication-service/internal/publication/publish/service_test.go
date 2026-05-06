package publish

import (
	"context"
	"fmt"
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

type fakeFileCopier struct {
	copies []fileCopyCall
	err    error
}

type fileCopyCall struct {
	srcBucket, srcKey, dstBucket, dstKey string
}

func (f *fakeFileCopier) CopyFile(_ context.Context, srcBucket, srcKey, dstBucket, dstKey string) (int64, error) {
	f.copies = append(f.copies, fileCopyCall{srcBucket, srcKey, dstBucket, dstKey})
	return 2048, f.err
}

func TestService_Handle_CopiesAdditionalFiles(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 100}},
	}}
	uploader := &fakeUploader{}
	fileCopier := &fakeFileCopier{}
	svc := NewService(copier, uploader, "https://public.example", discardLogger(), WithFileCopier(fileCopier))

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-001",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
		AdditionalFiles: []AdditionalFile{
			{ID: 67, Filename: "extra.pdf", S3URI: "https://store.example/src-bucket/path/to/extra.pdf"},
		},
	}
	result, err := svc.Handle(context.Background(), d)
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if len(fileCopier.copies) != 1 {
		t.Fatalf("expected 1 file copy, got %d", len(fileCopier.copies))
	}
	cp := fileCopier.copies[0]
	if cp.srcBucket != "src-bucket" {
		t.Errorf("srcBucket = %q", cp.srcBucket)
	}
	if cp.srcKey != "path/to/extra.pdf" {
		t.Errorf("srcKey = %q", cp.srcKey)
	}
	if cp.dstBucket != "pub" {
		t.Errorf("dstBucket = %q", cp.dstBucket)
	}
	if cp.dstKey != "out/extra.pdf" {
		t.Errorf("dstKey = %q", cp.dstKey)
	}
	_ = result
}

func TestService_Handle_AdditionalFileError_FailsPublish(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 100}}}}
	fileCopier := &fakeFileCopier{err: fmt.Errorf("not found")}
	svc := NewService(copier, &fakeUploader{}, "https://x", discardLogger(), WithFileCopier(fileCopier))

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-001",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
		AdditionalFiles: []AdditionalFile{
			{ID: 67, Filename: "fail.pdf", S3URI: "https://store.example/bucket/key.pdf"},
		},
	}
	_, err := svc.Handle(context.Background(), d)
	if err == nil {
		t.Fatal("expected error when additional file copy fails")
	}
}
