package s3

import (
	"context"
	"net/http"
	"net/http/httptest"
	"net/url"
	"sort"
	"testing"
	"time"

	s3types "github.com/aws/aws-sdk-go-v2/service/s3/types"

	"publication-service/internal/config"
	publish "publication-service/internal/publish"
)

func TestPublicReadACLForBucket(t *testing.T) {
	cases := []struct {
		name     string
		bucket   string
		wantACL  s3types.ObjectCannedACL
		wantUsed bool
	}{
		{
			name:     "dev openinfo bucket",
			bucket:   "dev-openinfopub",
			wantACL:  s3types.ObjectCannedACLPublicRead,
			wantUsed: true,
		},
		{
			name:     "production openinfo bucket",
			bucket:   "openinfopub",
			wantACL:  s3types.ObjectCannedACLPublicRead,
			wantUsed: true,
		},
		{
			name:     "other bucket",
			bucket:   "pd-published",
			wantUsed: false,
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := publicReadACLForBucket(tc.bucket)
			if !tc.wantUsed {
				if got != nil {
					t.Fatalf("publicReadACLForBucket(%q) = %v, want nil", tc.bucket, *got)
				}
				return
			}
			if got == nil {
				t.Fatalf("publicReadACLForBucket(%q) = nil, want %s", tc.bucket, tc.wantACL)
			}
			if *got != tc.wantACL {
				t.Fatalf("publicReadACLForBucket(%q) = %s, want %s", tc.bucket, *got, tc.wantACL)
			}
		})
	}
}

func TestCopyFile_BuildsCopySource(t *testing.T) {
	// CopyFile is tested via integration tests against localstack/minio.
	// Unit test verifies the method exists and interface compliance.
	var _ publish.FileCopier = (*Client)(nil)
}

func TestDeletePrefixDeletesObjectsIndividually(t *testing.T) {
	var deleted []string
	var sawMultiDelete bool
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch {
		case r.Method == http.MethodGet && r.URL.Path == "/public":
			if got := r.URL.Query().Get("list-type"); got != "2" {
				t.Fatalf("list-type = %q, want 2", got)
			}
			if got := r.URL.Query().Get("prefix"); got != "openinfo/pub/" {
				t.Fatalf("prefix = %q, want openinfo/pub/", got)
			}
			w.Header().Set("Content-Type", "application/xml")
			_, _ = w.Write([]byte(`<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult>
  <Name>public</Name>
  <Prefix>openinfo/pub/</Prefix>
  <KeyCount>3</KeyCount>
  <MaxKeys>1000</MaxKeys>
  <IsTruncated>false</IsTruncated>
  <Contents><Key>openinfo/pub/a.txt</Key><Size>1</Size></Contents>
  <Contents><Key>openinfo/pub/nested/b.txt</Key><Size>1</Size></Contents>
  <Contents><Key>openinfo/pub/</Key><Size>0</Size></Contents>
</ListBucketResult>`))
		case r.Method == http.MethodPost && r.URL.Path == "/public" && hasDeleteQuery(r.URL):
			sawMultiDelete = true
			http.Error(w, "multi-delete requires Content-MD5", http.StatusBadRequest)
		case r.Method == http.MethodDelete:
			deleted = append(deleted, r.URL.EscapedPath())
			w.WriteHeader(http.StatusNoContent)
		default:
			t.Fatalf("unexpected request: %s %s", r.Method, r.URL.String())
		}
	}))
	defer server.Close()

	client, err := NewClient(config.S3Config{
		Endpoint:        server.URL,
		Region:          "us-east-1",
		AccessKeyID:     "test-key",
		SecretAccessKey: "test-secret",
		UsePathStyle:    true,
		RequestTimeout:  time.Second,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	got, err := client.DeletePrefix(context.Background(), "public", "openinfo/pub/")
	if err != nil {
		t.Fatalf("DeletePrefix: %v", err)
	}
	if sawMultiDelete {
		t.Fatal("DeletePrefix used multi-object delete")
	}
	if got != 3 {
		t.Fatalf("DeletePrefix deleted %d objects, want 3", got)
	}
	sort.Strings(deleted)
	want := []string{"/public/openinfo/pub/", "/public/openinfo/pub/a.txt", "/public/openinfo/pub/nested/b.txt"}
	for i := range want {
		if deleted[i] != want[i] {
			t.Fatalf("deleted paths = %v, want %v", deleted, want)
		}
	}
}

func hasDeleteQuery(u *url.URL) bool {
	_, ok := u.Query()["delete"]
	return ok
}
