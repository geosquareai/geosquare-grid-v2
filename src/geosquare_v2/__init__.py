"""Geosquare V2 profile-driven metric grid core."""

from .codec import (
    BASE_2_MATRIX,
    BASE_5_MATRIX,
    MAX_LEVEL,
    ROOT_SIDE_M,
    SUBDIVISIONS,
    canonical_to_gid,
    gid_to_canonical,
)
from .batch import (
    encode_lonlat_arrow,
    encode_lonlat_numpy,
    encode_lonlat_pandas,
    encode_projected_arrow,
    encode_projected_numpy,
    encode_projected_pandas,
)
from .db import DbRegistryLoader, RegistryDomainSummary, list_registry_domains
from .errors import CandidateLimitExceededError, GeosquareError, GeometryDependencyError
from .geometry import projected_cell_geometry, wgs84_cell_geometry
from .polyfill import CoverageMode, polyfill, polyfill_stream
from .grid import GeosquareGrid
from .manifest import RegistryLoader
from .model import CanonicalCell, DomainProfile, ProjectedBounds
from .packing import pack_int64, unpack_int64
from .registry import DomainRegistry
from .release import ReleaseProfile

__all__ = [
    "BASE_2_MATRIX",
    "BASE_5_MATRIX",
    "CoverageMode",
    "MAX_LEVEL",
    "ROOT_SIDE_M",
    "SUBDIVISIONS",
    "CanonicalCell",
    "CandidateLimitExceededError",
    "DbRegistryLoader",
    "DomainProfile",
    "DomainRegistry",
    "GeosquareError",
    "GeometryDependencyError",
    "GeosquareGrid",
    "ProjectedBounds",
    "RegistryDomainSummary",
    "RegistryLoader",
    "ReleaseProfile",
    "list_registry_domains",
    "canonical_to_gid",
    "encode_lonlat_arrow",
    "encode_lonlat_numpy",
    "encode_lonlat_pandas",
    "encode_projected_arrow",
    "encode_projected_numpy",
    "encode_projected_pandas",
    "gid_to_canonical",
    "pack_int64",
    "polyfill",
    "polyfill_stream",
    "projected_cell_geometry",
    "unpack_int64",
    "wgs84_cell_geometry",
]

__version__ = "0.1.0"
