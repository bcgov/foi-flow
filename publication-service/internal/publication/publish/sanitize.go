package publish

import "strings"

// sanitizeFileName replaces spaces with underscores in the file-name
// portion (last path segment) of an S3 key. Directory segments are
// left unchanged.
func sanitizeFileName(key string) string {
	if key == "" {
		return key
	}
	slashIdx := strings.LastIndex(key, "/")
	if slashIdx == len(key)-1 {
		// Key ends with "/" — it's a directory marker, return as-is.
		return key
	}
	dir := ""
	name := key
	if slashIdx >= 0 {
		dir = key[:slashIdx+1]
		name = key[slashIdx+1:]
	}
	return dir + strings.ReplaceAll(name, " ", "_")
}
