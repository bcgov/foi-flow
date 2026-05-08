package publish

import "testing"

func TestSanitizeFileName(t *testing.T) {
	cases := []struct {
		name string
		key  string
		want string
	}{
		{name: "no spaces", key: "file.pdf", want: "file.pdf"},
		{name: "space in filename", key: "ABC-summary 1.pdf", want: "ABC-summary_1.pdf"},
		{name: "space in filename with path", key: "path/to/ABC-summary 1.pdf", want: "path/to/ABC-summary_1.pdf"},
		{name: "multiple spaces", key: "a  b  c.pdf", want: "a__b__c.pdf"},
		{name: "leading space", key: " leading.pdf", want: "_leading.pdf"},
		{name: "trailing space before ext", key: "trailing .pdf", want: "trailing_.pdf"},
		{name: "dir with space untouched", key: "dir with space/file.pdf", want: "dir with space/file.pdf"},
		{name: "empty string", key: "", want: ""},
		{name: "no filename just slash", key: "path/", want: "path/"},
		{name: "path with space in dir and file", key: "dir name/my file.pdf", want: "dir name/my_file.pdf"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := sanitizeFileName(tc.key)
			if got != tc.want {
				t.Errorf("sanitizeFileName(%q) = %q, want %q", tc.key, got, tc.want)
			}
		})
	}
}
