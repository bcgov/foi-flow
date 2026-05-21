package publish

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
)

// Class labels how an error should be handled by the consumer loop.
type Class string

const (
	ClassTransient Class = "transient"
	ClassPermanent Class = "permanent"
	ClassPoison    Class = "poison"
)

// PermanentError signals "do not retry — DLQ immediately".
type PermanentError struct{ Msg string }

func (e *PermanentError) Error() string { return e.Msg }

// TransientError signals "retry with backoff".
type TransientError struct{ Msg string }

func (e *TransientError) Error() string { return e.Msg }

// NewPermanent constructs a permanent error.
func NewPermanent(msg string) error { return &PermanentError{Msg: msg} }

// NewTransient constructs a transient error.
func NewTransient(msg string) error { return &TransientError{Msg: msg} }

// Classified is the structured form returned by Classify.
type Classified struct {
	Class   Class
	Message string
}

// RetryResult reports whether a transient failure was scheduled again or
// converted to a dead-letter state by retry policy.
type RetryResult struct {
	Dead  bool
	Class Class
}

// Classify turns any error into a (class, message) decision.
// Unknown errors default to transient — fail safe.
func Classify(err error) Classified {
	var p *PermanentError
	if errors.As(err, &p) {
		return Classified{Class: ClassPermanent, Message: p.Msg}
	}
	var tr *TransientError
	if errors.As(err, &tr) {
		return Classified{Class: ClassTransient, Message: tr.Msg}
	}
	return Classified{Class: ClassTransient, Message: err.Error()}
}

// ErrorHash is the poison-message dedup key.
func ErrorHash(class Class, message string) string {
	h := sha256.Sum256([]byte(string(class) + "\x00" + message))
	return hex.EncodeToString(h[:])
}
