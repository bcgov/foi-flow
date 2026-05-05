package s3

import (
	"context"
	"errors"
	"net"
	"testing"

	smithy "github.com/aws/smithy-go"

	pub "publication-service/internal/publish"
)

func TestClassifyS3Error(t *testing.T) {
	cases := []struct {
		name string
		err  error
		want pub.Class
	}{
		{"nil", nil, ""},
		{"context deadline", context.DeadlineExceeded, pub.ClassTransient},
		{"context canceled", context.Canceled, pub.ClassTransient},
		{"net timeout", &net.OpError{Op: "dial", Err: errTimeout{}}, pub.ClassTransient},
		{"no such bucket",
			&smithy.GenericAPIError{Code: "NoSuchBucket", Message: "missing"},
			pub.ClassPermanent},
		{"access denied",
			&smithy.GenericAPIError{Code: "AccessDenied", Message: "nope"},
			pub.ClassPermanent},
		{"invalid access key id",
			&smithy.GenericAPIError{Code: "InvalidAccessKeyId", Message: "nope"},
			pub.ClassPermanent},
		{"signature mismatch",
			&smithy.GenericAPIError{Code: "SignatureDoesNotMatch", Message: "nope"},
			pub.ClassPermanent},
		{"unknown error defaults to transient",
			errors.New("something exploded"),
			pub.ClassTransient},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := classifyS3Error(tc.err)
			if tc.err == nil {
				if got != nil {
					t.Fatalf("nil error classified as %v", got)
				}
				return
			}
			cl := pub.Classify(got)
			if cl.Class != tc.want {
				t.Fatalf("got class %q, want %q (err=%v)", cl.Class, tc.want, got)
			}
		})
	}
}

// errTimeout is a net.Error whose Timeout() returns true.
type errTimeout struct{}

func (errTimeout) Error() string   { return "i/o timeout" }
func (errTimeout) Timeout() bool   { return true }
func (errTimeout) Temporary() bool { return true }
