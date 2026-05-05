// Package redisstream implements messaging.Broker on top of Redis Streams.
package redisstream

import (
	"context"
	"crypto/tls"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"

	"publication-service/internal/messaging"
)

// Options configures the Redis client.
type Options struct {
	Addr     string
	Password string
	UseTLS   bool
}

// Broker is the Redis Streams implementation of messaging.Broker.
type Broker struct{ client *redis.Client }

// New constructs a Broker.
func New(opts Options) (*Broker, error) {
	cfg := &redis.Options{
		Addr:            opts.Addr,
		Password:        opts.Password,
		DialTimeout:     5 * time.Second,
		ReadTimeout:     30 * time.Second,
		WriteTimeout:    5 * time.Second,
		PoolTimeout:     10 * time.Second,
		ConnMaxIdleTime: 5 * time.Minute,
		MaxRetries:      3,
		MinRetryBackoff: 200 * time.Millisecond,
		MaxRetryBackoff: 2 * time.Second,
	}
	if opts.UseTLS {
		cfg.TLSConfig = &tls.Config{MinVersion: tls.VersionTLS12}
	}
	return &Broker{client: redis.NewClient(cfg)}, nil
}

// EnsureGroup creates a consumer group, ignoring BUSYGROUP.
func (b *Broker) EnsureGroup(ctx context.Context, stream, group string) error {
	err := b.client.XGroupCreateMkStream(ctx, stream, group, "$").Err()
	if err == nil {
		return nil
	}
	if strings.Contains(err.Error(), "BUSYGROUP") {
		return nil
	}
	return fmt.Errorf("redisstream.EnsureGroup: %w", err)
}

// Read blocks up to timeout for the next message; returns (nil, nil) on timeout.
func (b *Broker) Read(ctx context.Context, stream, group, consumer string, timeout time.Duration) (*messaging.StreamMessage, error) {
	res, err := b.client.XReadGroup(ctx, &redis.XReadGroupArgs{
		Group:    group,
		Consumer: consumer,
		Streams:  []string{stream, ">"},
		Count:    1,
		Block:    timeout,
	}).Result()
	if errors.Is(err, redis.Nil) {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("redisstream.Read: %w", err)
	}
	if len(res) == 0 || len(res[0].Messages) == 0 {
		return nil, nil
	}
	m := res[0].Messages[0]
	payload, _ := m.Values["payload"].(string)
	return &messaging.StreamMessage{ID: m.ID, Payload: []byte(payload)}, nil
}

// Ack acknowledges one message id.
func (b *Broker) Ack(ctx context.Context, stream, group, id string) error {
	if err := b.client.XAck(ctx, stream, group, id).Err(); err != nil {
		return fmt.Errorf("redisstream.Ack: %w", err)
	}
	return nil
}

// Publish appends one envelope to a stream with approximate MAXLEN trim.
func (b *Broker) Publish(ctx context.Context, stream string, payload []byte, maxLen int64) (string, error) {
	id, err := b.client.XAdd(ctx, &redis.XAddArgs{
		Stream: stream,
		MaxLen: maxLen,
		Approx: true,
		Values: map[string]any{"payload": string(payload)},
	}).Result()
	if err != nil {
		return "", fmt.Errorf("redisstream.Publish: %w", err)
	}
	return id, nil
}

// Trim runs XTRIM MINID up to the consumer group's last-delivered id.
func (b *Broker) Trim(ctx context.Context, stream, group string) error {
	groups, err := b.client.XInfoGroups(ctx, stream).Result()
	if err != nil {
		return fmt.Errorf("redisstream.Trim: groups: %w", err)
	}
	for _, g := range groups {
		if g.Name == group {
			if g.LastDeliveredID == "" || g.LastDeliveredID == "0-0" {
				return nil
			}
			if err := b.client.XTrimMinID(ctx, stream, g.LastDeliveredID).Err(); err != nil {
				return fmt.Errorf("redisstream.Trim: trim: %w", err)
			}
			return nil
		}
	}
	return nil
}

// Close shuts down the underlying client.
func (b *Broker) Close() error { return b.client.Close() }
