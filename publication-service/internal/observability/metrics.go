package observability

import (
	"context"

	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
)

// EventMetrics groups all event-flow telemetry instruments.
type EventMetrics struct {
	received           metric.Int64Counter
	processed          metric.Int64Counter
	retryCount         metric.Int64Histogram
	processingDuration metric.Float64Histogram
	outboxLag          metric.Float64Gauge
	consumerLag        metric.Int64Gauge
	deadLetter         metric.Int64Counter
	windowSkipped      metric.Int64Counter
}

// NewEventMetrics builds a metrics container from a Meter.
func NewEventMetrics(meter metric.Meter) (*EventMetrics, error) {
	rcv, err := meter.Int64Counter("events_received_total")
	if err != nil {
		return nil, err
	}
	prc, err := meter.Int64Counter("events_processed_total")
	if err != nil {
		return nil, err
	}
	rt, err := meter.Int64Histogram("event_retry_count")
	if err != nil {
		return nil, err
	}
	pd, err := meter.Float64Histogram("processing_duration_seconds")
	if err != nil {
		return nil, err
	}
	ol, err := meter.Float64Gauge("outbox_lag_seconds")
	if err != nil {
		return nil, err
	}
	cl, err := meter.Int64Gauge("consumer_lag")
	if err != nil {
		return nil, err
	}
	dl, err := meter.Int64Counter("dead_letter_total")
	if err != nil {
		return nil, err
	}
	ws, err := meter.Int64Counter("publish_window_skipped_total",
		metric.WithDescription("Events discarded because the publish window was closed"))
	if err != nil {
		return nil, err
	}
	return &EventMetrics{
		received: rcv, processed: prc, retryCount: rt,
		processingDuration: pd, outboxLag: ol, consumerLag: cl, deadLetter: dl,
		windowSkipped: ws,
	}, nil
}

func (m *EventMetrics) RecordReceived(ctx context.Context, eventType, tenantID string) {
	m.received.Add(ctx, 1, metric.WithAttributes(
		attribute.String("event_type", eventType),
		attribute.String("tenant_id", tenantID),
	))
}

func (m *EventMetrics) RecordProcessed(ctx context.Context, eventType, result string) {
	m.processed.Add(ctx, 1, metric.WithAttributes(
		attribute.String("event_type", eventType),
		attribute.String("result", result),
	))
}

func (m *EventMetrics) RecordRetryCount(ctx context.Context, n int) {
	m.retryCount.Record(ctx, int64(n))
}

func (m *EventMetrics) RecordProcessingDuration(ctx context.Context, eventType, phase string, seconds float64) {
	m.processingDuration.Record(ctx, seconds, metric.WithAttributes(
		attribute.String("event_type", eventType),
		attribute.String("phase", phase),
	))
}

func (m *EventMetrics) RecordOutboxLag(ctx context.Context, seconds float64) {
	m.outboxLag.Record(ctx, seconds)
}

func (m *EventMetrics) RecordConsumerLag(ctx context.Context, stream string, depth int64) {
	m.consumerLag.Record(ctx, depth, metric.WithAttributes(attribute.String("stream", stream)))
}

func (m *EventMetrics) RecordDeadLetter(ctx context.Context, eventType, lastErrorClass string) {
	m.deadLetter.Add(ctx, 1, metric.WithAttributes(
		attribute.String("event_type", eventType),
		attribute.String("last_error_class", lastErrorClass),
	))
}

func (m *EventMetrics) RecordWindowSkipped(ctx context.Context) {
	m.windowSkipped.Add(ctx, 1)
}
