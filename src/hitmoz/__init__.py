"""Fast async client and REST API for the HitMoz music catalog."""

from .client import HitMoz, Song, Result

__all__ = ["HitMoz", "Song", "Result"]
__version__ = "2.0.0"
