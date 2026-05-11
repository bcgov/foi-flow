package unpublish

import (
	"context"
	"time"

	"publication-service/internal/sitemapping"
)

type Service struct {
	repo    PublicRepository
	sitemap SitemapRemover
	store   ResultStore
	now     func() time.Time
}

func NewService(repo PublicRepository, sitemap SitemapRemover, store ResultStore) *Service {
	return &Service{
		repo:    repo,
		sitemap: sitemap,
		store:   store,
		now:     func() time.Time { return time.Now().UTC() },
	}
}

func (s *Service) Handle(ctx context.Context, req Request) (Result, error) {
	req, err := NormalizeRequest(req)
	if err != nil {
		return Result{}, err
	}
	if existing, ok, err := s.store.FindCompleted(ctx, req.Kind, req.PublicationID); err != nil {
		return Result{}, err
	} else if ok {
		// Close out the current claim so it doesn't stay in 'processing'
		_ = s.store.MarkSucceeded(ctx, req.SourceEventID, existing)
		return existing, nil
	}
	deleted, err := s.repo.DeletePrefix(ctx, req.PublicRepository.Bucket, req.PublicRepository.Prefix)
	if err != nil {
		return Result{}, err
	}
	sitemapResult, err := s.sitemap.Remove(ctx, sitemapping.RemovalRequest{
		Kind:          req.Kind,
		TenantID:      req.TenantID,
		PublicationID: req.PublicationID,
		PublicURL:     req.PublicURL,
		LastModified:  req.LastModified,
		SourceEventID: req.SourceEventID,
		CorrelationID: req.CorrelationID,
	})
	if err != nil {
		return Result{}, err
	}
	result := Result{
		Kind:                   req.Kind,
		TenantID:               req.TenantID,
		PublicationID:          req.PublicationID,
		PublicURL:              req.PublicURL,
		PublicRepositoryBucket: req.PublicRepository.Bucket,
		PublicRepositoryPrefix: req.PublicRepository.Prefix,
		ObjectsDeleted:         deleted,
		SitemapIndexKey:        sitemapResult.SitemapIndexKey,
		SitemapPageKey:         sitemapResult.SitemapPageKey,
		SitemapResult:          string(sitemapResult.Status),
		CompletedAt:            s.now(),
	}
	if err := s.store.MarkSucceeded(ctx, req.SourceEventID, result); err != nil {
		return Result{}, err
	}
	return result, nil
}
