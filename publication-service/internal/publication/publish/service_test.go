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
	svc, err := NewService(copier, uploader, "https://public.example", discardLogger())
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

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
	svc, err := NewService(copier, &fakeUploader{}, "https://x", discardLogger())
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		Source:      pub.S3Location{Bucket: "a", Prefix: "b/"},
		Destination: pub.S3Location{Bucket: "c", Prefix: "d/"},
	}
	_, err = svc.Handle(context.Background(), d)
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

type fakeDeleter struct {
	deleted []deleteCall
	err     error
}

type deleteCall struct {
	bucket, key string
}

func (f *fakeDeleter) Delete(_ context.Context, bucket, key string) error {
	f.deleted = append(f.deleted, deleteCall{bucket, key})
	return f.err
}

func TestService_Handle_CopiesAdditionalFiles(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 100}},
	}}
	uploader := &fakeUploader{}
	fileCopier := &fakeFileCopier{}
	deleter := &fakeDeleter{}
	svc, err := NewService(copier, uploader, "https://public.example", discardLogger(), WithFileCopier(fileCopier), WithDeleter(deleter))
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

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
	deleter := &fakeDeleter{}
	svc, err := NewService(copier, &fakeUploader{}, "https://x", discardLogger(), WithFileCopier(fileCopier), WithDeleter(deleter))
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-001",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
		AdditionalFiles: []AdditionalFile{
			{ID: 67, Filename: "fail.pdf", S3URI: "https://store.example/bucket/key.pdf"},
		},
	}
	_, err = svc.Handle(context.Background(), d)
	if err == nil {
		t.Fatal("expected error when additional file copy fails")
	}
}

func TestService_Handle_SanitizesBulkCopiedFileNames(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 2, BytesCopied: 300,
		Objects: []pub.CopiedObject{
			{Key: "ABC-summary 1.pdf", Size: 200},
			{Key: "clean.pdf", Size: 100},
		},
	}}
	uploader := &fakeUploader{}
	fileCopier := &fakeFileCopier{}
	deleter := &fakeDeleter{}
	svc, err := NewService(copier, uploader, "https://public.example", discardLogger(),
		WithFileCopier(fileCopier), WithDeleter(deleter))
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-002",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
	}
	result, err := svc.Handle(context.Background(), d)
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}

	// Verify the file with spaces was renamed.
	if len(fileCopier.copies) != 1 {
		t.Fatalf("expected 1 rename copy, got %d", len(fileCopier.copies))
	}
	cp := fileCopier.copies[0]
	if cp.srcBucket != "pub" || cp.srcKey != "out/ABC-summary 1.pdf" {
		t.Errorf("rename src = %s/%s", cp.srcBucket, cp.srcKey)
	}
	if cp.dstBucket != "pub" || cp.dstKey != "out/ABC-summary_1.pdf" {
		t.Errorf("rename dst = %s/%s", cp.dstBucket, cp.dstKey)
	}

	// Verify original was deleted.
	if len(deleter.deleted) != 1 {
		t.Fatalf("expected 1 delete, got %d", len(deleter.deleted))
	}
	del := deleter.deleted[0]
	if del.bucket != "pub" || del.key != "out/ABC-summary 1.pdf" {
		t.Errorf("delete = %s/%s", del.bucket, del.key)
	}

	_ = result

	// Check via uploaded HTML that contains the sanitized filename.
	html := uploader.uploaded["pub/out/HTH-002.html"]
	if html == nil {
		t.Fatal("HTML not uploaded")
	}
	htmlStr := string(html)
	if strings.Contains(htmlStr, "ABC-summary 1.pdf") {
		t.Error("HTML still contains original filename with space")
	}
	if !strings.Contains(htmlStr, "ABC-summary_1.pdf") {
		t.Error("HTML does not contain sanitized filename")
	}
}

func TestService_Handle_SanitizesAdditionalFileNames(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "doc.pdf", Size: 100}},
	}}
	uploader := &fakeUploader{}
	fileCopier := &fakeFileCopier{}
	deleter := &fakeDeleter{}
	svc, err := NewService(copier, uploader, "https://public.example", discardLogger(),
		WithFileCopier(fileCopier), WithDeleter(deleter))
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-003",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
		AdditionalFiles: []AdditionalFile{
			{ID: 1, Filename: "extra file.pdf", S3URI: "https://store.example/src-bucket/path/to/extra file.pdf"},
		},
	}
	result, err := svc.Handle(context.Background(), d)
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}

	// Verify the additional file was copied with sanitized name.
	if len(fileCopier.copies) != 1 {
		t.Fatalf("expected 1 file copy, got %d", len(fileCopier.copies))
	}
	cp := fileCopier.copies[0]
	if cp.dstKey != "out/extra_file.pdf" {
		t.Errorf("dstKey = %q, want %q", cp.dstKey, "out/extra_file.pdf")
	}

	_ = result
}

func TestService_Handle_NoSpaces_NoRename(t *testing.T) {
	copier := &fakeCopier{result: pub.CopyResult{
		ObjectsCopied: 1, BytesCopied: 100,
		Objects: []pub.CopiedObject{{Key: "clean.pdf", Size: 100}},
	}}
	uploader := &fakeUploader{}
	fileCopier := &fakeFileCopier{}
	deleter := &fakeDeleter{}
	svc, err := NewService(copier, uploader, "https://public.example", discardLogger(),
		WithFileCopier(fileCopier), WithDeleter(deleter))
	if err != nil {
		t.Fatalf("NewService: %v", err)
	}

	d := &Domain{
		Kind:        pub.KindOpenInfo,
		RequestID:   "HTH-004",
		Source:      pub.S3Location{Bucket: "raw", Prefix: "in/"},
		Destination: pub.S3Location{Bucket: "pub", Prefix: "out/"},
	}
	_, err = svc.Handle(context.Background(), d)
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}

	// No rename copies or deletes should have occurred.
	if len(fileCopier.copies) != 0 {
		t.Errorf("expected 0 rename copies, got %d", len(fileCopier.copies))
	}
	if len(deleter.deleted) != 0 {
		t.Errorf("expected 0 deletes, got %d", len(deleter.deleted))
	}
}

func TestNewService_ErrorWhenFileCopierWithoutDeleter(t *testing.T) {
	copier := &fakeCopier{}
	uploader := &fakeUploader{}
	_, err := NewService(copier, uploader, "https://x", discardLogger(), WithFileCopier(&fakeFileCopier{}))
	if err == nil {
		t.Fatal("expected error when fileCopier set without deleter")
	}
}

func TestNewService_ErrorWhenDeleterWithoutFileCopier(t *testing.T) {
	copier := &fakeCopier{}
	uploader := &fakeUploader{}
	_, err := NewService(copier, uploader, "https://x", discardLogger(), WithDeleter(&fakeDeleter{}))
	if err == nil {
		t.Fatal("expected error when deleter set without fileCopier")
	}
}

func TestNewService_OKWhenBothNil(t *testing.T) {
	copier := &fakeCopier{}
	uploader := &fakeUploader{}
	svc, err := NewService(copier, uploader, "https://x", discardLogger())
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if svc == nil {
		t.Fatal("service is nil")
	}
}

func TestNewService_OKWhenBothSet(t *testing.T) {
	copier := &fakeCopier{}
	uploader := &fakeUploader{}
	svc, err := NewService(copier, uploader, "https://x", discardLogger(),
		WithFileCopier(&fakeFileCopier{}), WithDeleter(&fakeDeleter{}))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if svc == nil {
		t.Fatal("service is nil")
	}
}
