# Geosquare Grid V2

A profile-driven, country-scoped hierarchical metric grid for durable spatial identifiers. Geosquare V2 encodes an exact square in a domain's declared projected CRS, with reproducible profile metadata, strict codecs, signed registry loading, fractional polygon coverage, vectorized interfaces, and warehouse UDF source generation.

> **Release status: candidate.** The bundled Indonesia (`ID`) and Vietnam (`VN`) profiles are signed candidate release artifacts. Do not mark them production or edit registry artifacts in place; regenerate, review, and re-sign a new candidate instead.

## What V2 guarantees

- **Canonical identity:** `(domain_code, level, x_idx, y_idx)` is the durable cell identity. A GID, packed `Int64`, and geometry are reversible encodings or derivations of it.
- **Exact projected geometry:** every cell is an exact square in the domain grid CRS. Reprojected WGS84 geometry is intended for display/interchange only.
- **Stable hierarchy:** levels `0`–`14` use fixed alternating subdivisions `[5, 2, 5, 2, …]`; level 9 is 1 km and level 14 is 5 m.
- **Explicit domain contract:** each country profile declares its CRS WKT2, equal-area CRS, root, reference epoch, scale metadata, and operational boundary.
- **Reproducible releases:** registry loading verifies the Ed25519 signature, artifact hashes, exact PROJ version/resources, and profile CRS definitions before returning any profile.
- **No lexical spatial assumptions:** use `domain`, `level`, `x_idx`, and `y_idx` for spatial windows and neighbours. GID lexical ranges are not geographic ranges.

V2 is intentionally **not wire-compatible** with V1 or the earlier international prototype. Store the versioned, domain-qualified identifier—`geosquare:v2:<domain>:<gid>`—in durable data, APIs, and events.

## Domains included

| Domain | Canonical grid CRS | Equal-area coverage CRS | Reference epoch |
|---|---|---|---:|
| `ID` — Indonesia | `GEOSQUARE:ID_SRGI2013_EQC_V2` | EPSG:8857 Equal Earth | 2012.0 |
| `VN` — Vietnam | `GEOSQUARE:VN_VN2000_LCC_V2` | EPSG:8857 Equal Earth | 2000.0 |

The full, authoritative CRS definitions and scale-error metadata are contained in the signed profiles, not abbreviated identifiers in this table.

## Installation

Requirements: Python 3.11+.

```zsh
# Scalar core plus signed registry loading
python -m pip install -e ".[registry]"

# Geometry/polyfill, NumPy/Pandas/Arrow, and tests
python -m pip install -e ".[analytics,registry,dev]"
```

Optional dependency groups are pinned in `pyproject.toml`:

| Extra | Provides |
|---|---|
| `registry` | Ed25519/RFC 8785 signature verification and PROJ resource checks |
| `geo` | PyProj and Shapely geometry operations |
| `batch` | NumPy, Pandas, and Apache Arrow adapters |
| `analytics` | Combined `geo` and `batch` runtime support |
| `dev` | Pytest test runner |

## Quick start: load a verified domain and encode a point

The registry trust anchor is supplied by the host application. The repository's `registry-trust.json` is a public-key example for the bundled candidate; production applications should manage their trusted public keys independently.

```python
import base64
import json
from pathlib import Path

from pyproj import CRS, Transformer

from geosquare_v2.grid import GeosquareGrid
from geosquare_v2.manifest import RegistryLoader

project_root = Path(".")
encoded_keys = json.loads((project_root / "registry-trust.json").read_text())
trust = {key_id: base64.b64decode(value) for key_id, value in encoded_keys.items()}

registry = RegistryLoader(
    project_root / "src/geosquare_v2/data/registry",
    trust,
).load()

profile = registry.get("ID")
grid = GeosquareGrid(profile)
to_grid = Transformer.from_crs(
    CRS.from_epsg(4326),
    CRS.from_user_input(profile.crs_wkt2),
    always_xy=True,
)

cell = grid.canonical_from_lonlat(106.8456, -6.2088, level=9, transformer=to_grid)
gid = grid.gid_from_canonical(cell)

print(grid.uri(cell))          # geosquare:v2:ID:<gid>
print(grid.pack(cell))         # non-negative signed Int64
print(grid.projected_bounds(cell))
```

`always_xy=True` is required when transforming longitude/latitude. Projected input is valid on the **closed** root extent; the outer maximum root edge belongs to the final cell at that level. Internal cell intervals are half-open.

A bare GID is only valid where domain and version are fixed by the API contract. The level-0 root GID is the empty string (`""`).

## Core operations

```python
# Decode and hierarchy/topology operations
decoded = grid.canonical_from_gid(gid)
parent = grid.parent(decoded)
children = grid.children(parent)       # 4 or 25 children, depending on the next level
neighbours = grid.k_ring(decoded, 1)   # Moore neighbourhood, clipped to the mathematical root

# Lossless signed Int64 round trip
packed = grid.pack(decoded)
assert grid.unpack(packed) == decoded
```

Country-boundary filtering is deliberately not implicit in core indexing. The mathematical root remains complete; applications that need an operational boundary predicate must apply and name it explicitly.

## Geometry and fractional polyfill

The authoritative shape is the exact projected square. Use densified WGS84 geometry when a geographic display shape is needed.

```python
from shapely.geometry import Polygon

from geosquare_v2.geometry import projected_cell_geometry, wgs84_cell_geometry
from geosquare_v2.polyfill import CoverageMode, polyfill

projected_square = projected_cell_geometry(grid, gid)
wgs84_polygon = wgs84_cell_geometry(grid, gid, max_segment_length_m=25_000)

# Input polygon coordinates are WGS84 longitude/latitude.
polygon = Polygon([
    (106.80, -6.24),
    (106.89, -6.24),
    (106.89, -6.16),
    (106.80, -6.16),
    (106.80, -6.24),
])

coverage = polyfill(
    grid,
    polygon,
    "EPSG:4326",
    level=9,
    coverage_mode=CoverageMode.EQUAL_AREA,
    min_coverage=0.01,
    max_candidate_limit=100_000,
)
# (bare_gid, coverage_ratio) pairs in deterministic row-major order
```

`GRID_PLANAR` calculates the ratio in the grid CRS. `EQUAL_AREA` calculates it through the profile's verified equal-area CRS and should be used for coastal, cross-projection, or published statistical coverage. Polyfill normalizes polygonal input, clips it to the root, applies its candidate limit **before** enumeration, and never silently filters by the country boundary.

## Vectorized data interfaces

NumPy is the numeric reference implementation for batch encoding. Pandas and Arrow adapters use the same vectorized kernels.

```python
import numpy as np
import pandas as pd
import pyarrow as pa

from geosquare_v2.batch import (
    encode_lonlat_numpy,
    encode_projected_arrow,
    encode_projected_pandas,
)

# WGS84 arrays -> canonical indices, bare GIDs, and signed Int64 values
encoded = encode_lonlat_numpy(
    grid,
    np.array([106.8456, 106.8460]),
    np.array([-6.2088, -6.2090]),
    level=9,
)
print(encoded.gid, encoded.packed_id)

# Projected-coordinate DataFrame and Arrow table adapters
frame = pd.DataFrame({"x_m": [0.0], "y_m": [0.0]})
pandas_result = encode_projected_pandas(grid, frame, "x_m", "y_m", level=9)
arrow_result = encode_projected_arrow(grid, pa.table(frame), "x_m", "y_m", level=9)
```

Available adapters are `encode_projected_numpy`, `encode_lonlat_numpy`, `encode_projected_pandas`, `encode_lonlat_pandas`, `encode_projected_arrow`, and `encode_lonlat_arrow`. Batch operations preserve scalar root-edge semantics and return `domain`, `level`, `x_idx`, `y_idx`, `gid`, and `packed_id` fields.

## Warehouse UDF source generation

Generate SQL/JavaScript source from a **verified** `ReleaseProfile`:

```python
from geosquare_v2.warehouse import (
    render_bigquery_projected_encoder,
    render_snowflake_projected_encoder,
    render_postgis_projected_encoder,
)

bigquery_sql = render_bigquery_projected_encoder(profile, routine="my_dataset.geosquare_id_encode")
snowflake_sql = render_snowflake_projected_encoder(profile, routine="GEOSQUARE_ID_ENCODE")
postgis_sql = render_postgis_projected_encoder(profile, routine="geosquare_id_encode")
```

Generated UDFs encode **projected X/Y metres in the profile grid CRS**; they do not perform profile-specific WGS84/PROJ transformations. Transform longitude/latitude before calling them. BigQuery and Snowflake JavaScript UDFs emit packed IDs as strings because JavaScript numbers cannot safely represent every V2 signed `Int64`; the PostGIS function returns native `BIGINT`.

## Registry release and governance

The registry loader is fail-closed. It checks the manifest signature, profile/boundary/scale hashes, CRS parseability, and the exact signed PROJ environment before profiles are available. A local PROJ upgrade or any artifact change requires a fresh generated and signed candidate.

Never commit, distribute, or attach an Ed25519 private key. To create a new candidate after approved profile/boundary changes:

```zsh
.venv/bin/python scripts/generate_release_candidates.py
.venv/bin/python scripts/sign_registry.py \
  --private-key /secure/path/geosquare-registry-private.pem \
  --input src/geosquare_v2/data/registry/registry.unsigned.v2.json \
  --output src/geosquare_v2/data/registry/registry.v2.json \
  --key-id geosquare-registry-2026-08
```

Review the generated diff, CRS definitions, distortion metadata, boundary provenance, and release authorization before signing. See [RELEASE_CANDIDATE.md](RELEASE_CANDIDATE.md) and [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) for the full process and rationale.

## Validation

```zsh
.venv/bin/python -m compileall -q src scripts tests
.venv/bin/pytest -q -W error::DeprecationWarning
.venv/bin/python -m pip check
```

The focused suite covers scalar/GID/packed consistency, projected and WGS84 geometry, planar/equal-area fractional coverage, candidate limits, NumPy/Pandas/Arrow equivalence, UDF source invariants, and end-to-end paths through the signed ID/VN candidate profiles.

## Project layout

```text
src/geosquare_v2/                 Package source
  data/registry/                  Signed candidate registry, profiles, boundaries, scale metadata
  geometry.py                     Exact projected and densified WGS84 geometry
  polyfill.py                     Bounded fractional coverage
  batch.py                        NumPy, Pandas, Arrow encoders
  warehouse.py                    BigQuery, Snowflake, PostGIS UDF renderers
scripts/                          Candidate generation and signing tools
tests/                            Focused conformance tests
V2SPECS.md                        Normative V2 contract
ARCHITECTURE_DECISIONS.md          Architecture decision record
RELEASE_CANDIDATE.md               Candidate release instructions
```

## Further reading

- [Crucial logic and CRS guide](CRUCIAL_LOGIC.md)
- [V2 specification](V2SPECS.md)
- [Architecture decisions](ARCHITECTURE_DECISIONS.md)
- [Candidate release instructions](RELEASE_CANDIDATE.md)
- [Boundary source attribution](src/geosquare_v2/data/registry/boundaries/SOURCES.md)
