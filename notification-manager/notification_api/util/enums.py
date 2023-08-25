"""Enum definitions."""
from enum import Enum


class ServiceKey(Enum):
    """Authorization header types."""

    pdfstitchforhamrs = "pdfstitchforhamrs"
    pdfstitchforredline = "pdfstitchforredline"
