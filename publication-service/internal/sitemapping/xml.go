package sitemapping

import (
	"bytes"
	"encoding/xml"

	pub "publication-service/internal/publish"
)

const sitemapNS = "http://www.sitemaps.org/schemas/sitemap/0.9"

type URLEntry struct {
	Loc     string `xml:"loc"`
	LastMod string `xml:"lastmod"`
}

type URLSet struct {
	XMLName xml.Name   `xml:"urlset"`
	Xmlns   string     `xml:"xmlns,attr"`
	URLs    []URLEntry `xml:"url"`
}

func NewURLSet() URLSet {
	return URLSet{Xmlns: sitemapNS}
}

func ParseURLSet(raw []byte) (URLSet, error) {
	if len(bytes.TrimSpace(raw)) == 0 {
		return NewURLSet(), nil
	}
	var out URLSet
	if err := xml.Unmarshal(raw, &out); err != nil {
		return URLSet{}, pub.NewTransient("sitemap page XML parse failed: " + err.Error())
	}
	out.Xmlns = sitemapNS
	return out, nil
}

func (s *URLSet) Contains(loc string) bool {
	for _, u := range s.URLs {
		if u.Loc == loc {
			return true
		}
	}
	return false
}

func (s *URLSet) Remove(loc string) bool {
	for i, u := range s.URLs {
		if u.Loc == loc {
			s.URLs = append(s.URLs[:i], s.URLs[i+1:]...)
			return true
		}
	}
	return false
}

func (s URLSet) Empty() bool {
	return len(s.URLs) == 0
}

func (s *URLSet) Append(entry URLEntry) {
	s.URLs = append(s.URLs, entry)
}

func (s URLSet) Render() ([]byte, error) {
	s.Xmlns = sitemapNS
	return xml.MarshalIndent(s, "", "  ")
}

type SitemapEntry struct {
	Loc     string `xml:"loc"`
	LastMod string `xml:"lastmod"`
}

type SitemapIndex struct {
	XMLName  xml.Name       `xml:"sitemapindex"`
	Xmlns    string         `xml:"xmlns,attr"`
	Sitemaps []SitemapEntry `xml:"sitemap"`
}

func NewSitemapIndex() SitemapIndex {
	return SitemapIndex{Xmlns: sitemapNS}
}

func ParseSitemapIndex(raw []byte) (SitemapIndex, error) {
	if len(bytes.TrimSpace(raw)) == 0 {
		return NewSitemapIndex(), nil
	}
	var out SitemapIndex
	if err := xml.Unmarshal(raw, &out); err != nil {
		return SitemapIndex{}, pub.NewTransient("sitemap index XML parse failed: " + err.Error())
	}
	out.Xmlns = sitemapNS
	return out, nil
}

func (s *SitemapIndex) Append(entry SitemapEntry) {
	s.Sitemaps = append(s.Sitemaps, entry)
}

func (s *SitemapIndex) Remove(loc string) bool {
	for i, entry := range s.Sitemaps {
		if entry.Loc == loc {
			s.Sitemaps = append(s.Sitemaps[:i], s.Sitemaps[i+1:]...)
			return true
		}
	}
	return false
}

func (s SitemapIndex) Render() ([]byte, error) {
	s.Xmlns = sitemapNS
	return xml.MarshalIndent(s, "", "  ")
}
