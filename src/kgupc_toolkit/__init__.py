"""Versioned KGUPC templates and PDF generation, independent of any contest."""

__version__ = "1.0.0"

from .resources import package_digest, resource_root, verify_lock

__all__ = ["__version__", "package_digest", "resource_root", "verify_lock"]
