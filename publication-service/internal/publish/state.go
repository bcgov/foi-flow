// Package publish contains shared types for both the openinfo and
// proactivedisclosure publish pipelines.
package publish

// State is the lifecycle stage of a publish_request row.
type State string

const (
	StatePending      State = "pending"
	StateProcessing   State = "processing"
	StatePendingRetry State = "pending_retry"
	StateCompleted    State = "completed"
	StateDead         State = "dead"
)

// CanTransition reports whether a row can move from receiver to next.
func (s State) CanTransition(next State) bool {
	switch s {
	case StatePending, StatePendingRetry:
		return next == StateProcessing
	case StateProcessing:
		switch next {
		case StateCompleted, StatePendingRetry, StateDead:
			return true
		}
	}
	return false
}

func (s State) String() string { return string(s) }
