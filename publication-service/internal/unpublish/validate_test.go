package unpublish

import (
	"testing"

	pub "publication-service/internal/publish"
)

func TestNormalizeRequest_CanonicalizesPrefix(t *testing.T) {
	req, err := NormalizeRequest(Request{
		Kind:          pub.KindOpenInfoUnpublish,
		TenantID:      " tenant ",
		PublicationID: " pub ",
		PublicURL:     " https://example/item.html ",
		PublicRepository: PublicRepositoryLocation{
			Bucket: " public ",
			Prefix: "/openinfo/REQ-1/",
		},
	})
	if err != nil {
		t.Fatalf("NormalizeRequest: %v", err)
	}
	if req.PublicRepository.Prefix != "openinfo/REQ-1/" {
		t.Fatalf("prefix = %q", req.PublicRepository.Prefix)
	}
	if req.TenantID != "tenant" || req.PublicationID != "pub" || req.PublicURL != "https://example/item.html" {
		t.Fatalf("request was not trimmed: %#v", req)
	}
}

func TestNormalizeRequest_RejectsMissingRequiredFields(t *testing.T) {
	_, err := NormalizeRequest(Request{Kind: pub.KindOpenInfoUnpublish})
	if err == nil {
		t.Fatal("expected missing tenant_id error")
	}
}

func TestNormalizeRequest_RejectsUnsupportedKind(t *testing.T) {
	_, err := NormalizeRequest(Request{Kind: pub.KindOpenInfo})
	if err == nil {
		t.Fatal("expected unsupported kind error")
	}
}
