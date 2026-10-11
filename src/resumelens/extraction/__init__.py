"""Stage 1: résumé information extraction with regular expressions."""

from .extraction import ExtractionMatch, ExtractionResult, extract_resume

__all__ = ["ExtractionMatch", "ExtractionResult", "extract_resume"]
