package unpublish

import (
	"context"
	"errors"
	"testing"

	pub "publication-service/internal/publish"
	"publication-service/internal/sitemapping"
)

type fakePublicRepo struct {
	deletedBucket string
	deletedPrefix string
	count         int
	err           error
}

func (f *fakePublicRepo) DeletePrefix(_ context.Context, bucket, prefix string) (int, error) {
	f.deletedBucket = bucket
	f.deletedPrefix = prefix
	return f.count, f.err
}

type fakeSitemapRemover struct {
	called bool
	err    error
}

func (f *fakeSitemapRemover) Remove(_ context.Context, req sitemapping.RemovalRequest) (sitemapping.RemovalResult, error) {
	f.called = true
	return sitemapping.RemovalResult{
		Kind:            req.Kind,
		TenantID:        req.TenantID,
		PublicationID:   req.PublicationID,
		PublicURL:       req.PublicURL,
		SitemapIndexKey: "sitemap/index.xml",
		SitemapPageKey:  "sitemap/page.xml",
		Status:          sitemapping.RemovalStatusRemoved,
	}, f.err
}

type fakeResultStore struct {
	marked              Result
	findCompletedKind   pub.Kind
	findCompletedTenant string
	findCompletedCorrID string
	findCompletedCalls  int
}

func (f *fakeResultStore) FindCompleted(_ context.Context, kind pub.Kind, tenantID string, correlationID string) (Result, bool, error) {
	f.findCompletedKind = kind
	f.findCompletedTenant = tenantID
	f.findCompletedCorrID = correlationID
	f.findCompletedCalls++
	return Result{}, false, nil
}

func (f *fakeResultStore) MarkSucceeded(_ context.Context, _ string, result Result) error {
	f.marked = result
	return nil
}

func TestService_HandleDeletesPrefixThenRemovesSitemap(t *testing.T) {
	repo := &fakePublicRepo{count: 2}
	sitemap := &fakeSitemapRemover{}
	store := &fakeResultStore{}
	svc := NewService(repo, sitemap, store)

	got, err := svc.Handle(context.Background(), Request{
		Kind:          pub.KindOpenInfoUnpublish,
		TenantID:      "tenant",
		PublicationID: "pub",
		PublicURL:     "https://example/pub.html",
		PublicRepository: PublicRepositoryLocation{
			Bucket: "public",
			Prefix: "openinfo/pub",
		},
		SourceEventID: "event-1",
	})
	if err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if repo.deletedPrefix != "openinfo/pub/" || !sitemap.called {
		t.Fatalf("delete/removal order not observed: repo=%#v sitemap=%#v", repo, sitemap)
	}
	if got.ObjectsDeleted != 2 || got.SitemapResult != "removed" {
		t.Fatalf("result = %#v", got)
	}
	if store.marked.PublicationID != "pub" {
		t.Fatalf("result not stored: %#v", store.marked)
	}
}

func TestService_HandleFindsCompletedByKindTenantAndCorrelationID(t *testing.T) {
	repo := &fakePublicRepo{count: 2}
	sitemap := &fakeSitemapRemover{}
	store := &fakeResultStore{}
	svc := NewService(repo, sitemap, store)

	req := Request{
		Kind:          pub.KindOpenInfoUnpublish,
		TenantID:      "tenant",
		PublicationID: "pub",
		PublicURL:     "https://example/pub.html",
		PublicRepository: PublicRepositoryLocation{
			Bucket: "public",
			Prefix: "openinfo/pub",
		},
		SourceEventID: "event-1",
		CorrelationID: "corr-1",
	}
	if _, err := svc.Handle(context.Background(), req); err != nil {
		t.Fatalf("Handle: %v", err)
	}
	if store.findCompletedCalls != 1 {
		t.Fatalf("FindCompleted calls = %d, want 1", store.findCompletedCalls)
	}
	if store.findCompletedKind != req.Kind {
		t.Fatalf("FindCompleted kind = %q, want %q", store.findCompletedKind, req.Kind)
	}
	if store.findCompletedTenant != req.TenantID {
		t.Fatalf("FindCompleted tenant = %q, want %q", store.findCompletedTenant, req.TenantID)
	}
	if store.findCompletedCorrID != req.CorrelationID {
		t.Fatalf("FindCompleted correlation = %q, want %q", store.findCompletedCorrID, req.CorrelationID)
	}
}

func TestService_HandleDeleteFailurePreventsSitemapRemoval(t *testing.T) {
	repo := &fakePublicRepo{err: errors.New("delete failed")}
	sitemap := &fakeSitemapRemover{}
	svc := NewService(repo, sitemap, &fakeResultStore{})

	_, err := svc.Handle(context.Background(), Request{
		Kind:          pub.KindOpenInfoUnpublish,
		TenantID:      "tenant",
		PublicationID: "pub",
		PublicURL:     "https://example/pub.html",
		PublicRepository: PublicRepositoryLocation{
			Bucket: "public",
			Prefix: "openinfo/pub",
		},
	})
	if err == nil {
		t.Fatal("expected delete failure")
	}
	if sitemap.called {
		t.Fatal("sitemap removal should not run after delete failure")
	}
}
