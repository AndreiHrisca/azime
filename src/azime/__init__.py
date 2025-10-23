"""
Azime — Modular AI Framework

This package contains the cognitive modules that form Azime's architecture:
core, audio, vision, memory, reasoner, persona, and context.
"""

__version__ = "0.1.0"

from importlib import metadata

try:
    __version__ = metadata.version("azime")
except metadata.PackageNotFoundError:
    pass