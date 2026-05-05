package s3

import (
	"testing"

	s3types "github.com/aws/aws-sdk-go-v2/service/s3/types"
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
