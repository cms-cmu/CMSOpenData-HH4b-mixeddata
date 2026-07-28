"""
File storage abstractions and utilities.

This module provides abstractions for working with different storage systems,
including local filesystem and remote storage like EOS.
"""

from .eos import EOS, EOSError, PathLike, load, save

__all__ = [
    "EOS",
    "EOSError", 
    "PathLike",
    "load",
    "save",
]
