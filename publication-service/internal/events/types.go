package events

// Event type identifiers (dot notation per the EDA skill).
const (
	TypePublicationPublishRequested    = "publication.publish.requested"
	TypePublicationPublishCompleted    = "publication.publish.completed"
	TypePublicationSitemappingRequested = "publication.sitemapping.requested"
	TypePublicationSitemappingCompleted = "publication.sitemapping.completed"
	TypePublicationUnpublishRequested  = "publication.unpublish.requested"
	TypePublicationUnpublishCompleted  = "publication.unpublish.completed"
)

// SchemaVersionV1 is the only payload schema version this service understands today.
const SchemaVersionV1 = "1.0.0"
