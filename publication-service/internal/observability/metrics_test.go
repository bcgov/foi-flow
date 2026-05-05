package observability

import (
	"context"
	"testing"

	"go.opentelemetry.io/otel/metric/noop"
)

func TestNewEventMetrics(t *testing.T) {
	m, err := NewEventMetrics(noop.NewMeterProvider().Meter("test"))
	if err != nil {
		t.Fatalf("NewEventMetrics: %v", err)
	}
	m.RecordReceived(context.Background(), "openinfo.publish.requested", "tenant-x")
	m.RecordProcessed(context.Background(), "openinfo.publish.requested", "completed")
	m.RecordRetryCount(context.Background(), 3)
	m.RecordProcessingDuration(context.Background(), "openinfo.publish.requested", "handler", 0.42)
	m.RecordOutboxLag(context.Background(), 12.3)
	m.RecordConsumerLag(context.Background(), "openinfo.publish.requested", 1500)
	m.RecordDeadLetter(context.Background(), "openinfo.publish.requested", "permanent")
}
