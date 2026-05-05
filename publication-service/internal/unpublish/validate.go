package unpublish

import (
	"strings"

	pub "publication-service/internal/publish"
)

func NormalizeRequest(req Request) (Request, error) {
	switch req.Kind {
	case pub.KindOpenInfoUnpublish, pub.KindProactiveDisclosureUnpublish:
	case pub.KindUnknown:
		return Request{}, pub.NewPermanent("unpublish: kind is required")
	default:
		return Request{}, pub.NewPermanent("unpublish: unsupported kind " + string(req.Kind))
	}

	req.TenantID = strings.TrimSpace(req.TenantID)
	req.PublicationID = strings.TrimSpace(req.PublicationID)
	req.PublicURL = strings.TrimSpace(req.PublicURL)
	req.PublicRepository.Bucket = strings.TrimSpace(req.PublicRepository.Bucket)
	req.PublicRepository.Prefix = strings.Trim(req.PublicRepository.Prefix, "/")
	if req.PublicRepository.Prefix != "" {
		req.PublicRepository.Prefix += "/"
	}

	if req.TenantID == "" {
		return Request{}, pub.NewPermanent("unpublish: tenant_id is required")
	}
	if req.PublicationID == "" {
		return Request{}, pub.NewPermanent("unpublish: publication_id is required")
	}
	if req.PublicURL == "" {
		return Request{}, pub.NewPermanent("unpublish: public_url is required")
	}
	if req.PublicRepository.Bucket == "" {
		return Request{}, pub.NewPermanent("unpublish: public repository bucket is required")
	}
	if req.PublicRepository.Prefix == "" {
		return Request{}, pub.NewPermanent("unpublish: public repository prefix is required")
	}
	return req, nil
}
