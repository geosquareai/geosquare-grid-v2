# GeoSquare Grid V2 handover

**Date:** 2026-09-18  
**Repository:** `geosquare-grid-v2`  
**Package name:** `geosquare-grid-v2`  
**Python import:** `geosquare_v2`  
**Current release:** `0.1.0` candidate  
**Current profile version:** `2.0.0-rc.2-asean`

This document explains the current state, the important decisions, the remaining work, and the main things to watch before publishing.

## 1. Current Git state

Both remote branches currently point to the release commit:

```text
main        5b98c6d
 db_registry 5b98c6d
```

Commit message:

```text
Prepare ASEAN V2 release candidate
```

The old signing PEM files were purged from reachable history:

```text
geosquare-registry-private.pem
geosquare-registry-public.pem
```

The old private key must still be considered compromised. Do not reuse it.

The new private key is outside the repository. It must stay there and must never be committed or distributed.

## 2. Current uncommitted work

At handover time, the following work is not yet committed:

```text
CELL_DATASET_CONTRACT.md
schemas/cell-dataset-manifest-v1.schema.json
README.md
DATA_TO_GRID_CONTRACT.md
docs/README.md
docs/03_DATA_AND_AGGREGATION.md
```

There is also a local `dist/` directory containing build artifacts. It should normally stay uncommitted.

`.DS_Store` is also modified locally. Do not include it in a release commit.

The dataset contract work is the next development step. Review and commit it before implementing the S3 reader and writer.

## 3. Current registry

The signed candidate registry contains all 11 ASEAN domains:

```text
BN  Brunei Darussalam
KH  Cambodia
ID  Indonesia
LA  Lao PDR
MY  Malaysia
MM  Myanmar
PH  Philippines
SG  Singapore
TH  Thailand
TL  Timor-Leste
VN  Viet Nam
```

Registry files:

```text
src/geosquare_v2/db/registry.db
src/geosquare_v2/db/registry.db.sig
registry.v2.json
registry-trust.json
```

The registry status is still:

```text
candidate
```

The registry is not yet a final legal or geodetic production release.

## 4. What has been implemented

### Core grid

- Canonical identity:

  ```text
  (domain_code, level, x_idx, y_idx)
  ```

- Versioned URI:

  ```text
  geosquare:v2:<domain>:<gid>
  ```

- Levels 0–14.
- Alternating 5x5 and 2x2 hierarchy.
- Level 12 is nominally 50 m in the grid CRS.
- Level 14 is nominally 5 m in the grid CRS.
- Exact projected square geometry.
- WGS84 display geometry with edge densification.
- Parent and child operations.
- Integer neighbour, ring, and disk operations.
- Same-level grid distance.
- Strict GID validation.
- Packed signed Int64 encoding.

### Registry

- Signed SQLite registry.
- Ed25519 detached database signature.
- Profile hash checks.
- Scale metadata hash checks.
- Optional boundary hash checks.
- CRS WKT2 validation.
- Exact PROJ version/resource checks.
- All 11 ASEAN candidate domains.

### Boundary policies

Implemented policies:

```text
COVERS_POINT
CENTROID_COVERED
INTERSECTS
MIN_COVERAGE
```

Core grid operations remain boundary-neutral.

Boundary filtering is explicit in point, polygon, line, and neighbourhood operations.

### Data conversion

Implemented public names:

```text
point_to_cell
polygon_to_cells
polygon_to_cell
line_to_cells
cell_to_geometry
cells_to_geometry
table_to_cells
aggregate_to_cells
cell_neighbours
cell_distance
```

Older names remain aliases:

```text
index_point
polyfill
neighbourhood
distance
```

### Table and aggregation

Implemented:

- CSV input;
- XLSX input;
- Parquet input;
- Pandas DataFrame input;
- selected source-field retention;
- optional cell geometry output;
- chunked CSV processing;
- numeric aggregation;
- categorical aggregation;
- ordinal aggregation; and
- range aggregation.

### V1 migration

Implemented:

- isolated V1 GID decoding;
- point migration using original coordinates;
- centroid fallback when coordinates are missing;
- area migration through V2 polyfill;
- one-to-many mappings; and
- migration provenance.

### Documentation

The canonical documentation entry point is:

```text
docs/README.md
```

The docs cover:

- overview;
- API;
- data conversion;
- aggregation;
- boundaries;
- migration;
- country profiles;
- grid-system comparisons;
- release and security; and
- dataset storage contract.

## 5. Validation already completed

The pinned environment is:

```text
Python 3.14
PyProj 3.7.2
Shapely 2.1.2
NumPy 2.3.5
Pandas 2.3.3
PyArrow 22.0.0
OpenPyXL 3.1.5
Pytest 8.4.2
Cryptography 50.0.0
RFC 8785 0.1.4
```

The full test suite passed:

```text
144 passed
```

The following also passed:

- `pip check`;
- source-tree 11-domain registry load;
- boundary verification;
- wheel install;
- sdist install;
- 11-domain registry load from installed wheel;
- 11-domain registry load from installed sdist;
- `twine check dist/*`;
- package metadata checks;
- local Markdown link checks;
- JSON artifact parsing;
- profile and boundary hash checks; and
- Git diff checks.

Build artifacts:

```text
dist/geosquare_grid_v2-0.1.0-py3-none-any.whl
dist/geosquare_grid_v2-0.1.0.tar.gz
```

The wheel and sdist contain the package, registry, signature, full boundaries, metadata, and documentation included by `MANIFEST.in`.

## 6. Highest-priority next work

## Priority 1: finish the cell dataset format

The current draft files are:

```text
CELL_DATASET_CONTRACT.md
schemas/cell-dataset-manifest-v1.schema.json
```

They define:

- `cell_values` datasets;
- `cell_contributions` datasets;
- compact `gid + value` files;
- optional `packed_id`, `x_idx`, and `y_idx`;
- value-field metadata;
- coverage metadata;
- source metadata;
- storage metadata;
- provenance; and
- validation rules.

Next implementation steps:

1. Add a manifest value object or parser.
2. Validate manifest fields at runtime.
3. Validate the Parquet schema against the manifest.
4. Validate GIDs against the trusted profile.
5. Validate duplicate rules.
6. Validate coverage and length ratios.
7. Embed the manifest in Parquet metadata.
8. Write a sidecar `manifest.json`.
9. Add local Parquet round-trip tests.
10. Add a clean example dataset.

### Important schema decision

The minimum compact dataset is:

```text
gid
value fields...
```

The manifest must provide:

```text
domain
level
profile version
registry version
value semantics
aggregation rule
boundary policy
coverage mode
```

Without this metadata, a bare GID is ambiguous.

### Package attention

`CELL_DATASET_CONTRACT.md` and `schemas/` currently need a package-distribution decision.

If users need them after `pip install`, either:

- move them under `docs/` or package data; or
- add them explicitly to `MANIFEST.in` and package resources.

Do not assume a root Markdown file automatically appears in the wheel.

## Priority 2: implement `CellDataset`

After the schema is stable, add a first-class dataset object.

Suggested API:

```python
dataset = table_to_cells(...)
dataset.write("s3://bucket/path/")

dataset = read_cell_dataset("s3://bucket/path/")
dataset.validate()
dataset.query(...)
dataset.with_geometry(...)
dataset.aggregate(...)
```

Suggested modules:

```text
src/geosquare_v2/dataset.py
src/geosquare_v2/manifest.py
src/geosquare_v2/storage.py
```

Keep S3 support optional.

Do not add `boto3` to the core package unless there is a clear need. Prefer an optional filesystem layer such as `fsspec`/`s3fs`, or accept file-like objects and let the application configure S3 access.

## Priority 3: add dataset query support

Users will often need only the cells in a map viewport.

Add:

```python
query_cell_dataset(
    "s3://bucket/path/",
    bbox=(min_lon, min_lat, max_lon, max_lat),
    domain="ID",
    level=12,
)
```

The query layer should:

- read the manifest first;
- validate the requested domain and level;
- transform the query bounds to the grid CRS;
- calculate an x/y candidate window;
- use Parquet predicate pushdown where possible; and
- avoid constructing every cell geometry.

A queryable dataset should include:

```text
x_idx
y_idx
packed_id
```

A compact distribution can keep only `gid`.

## Priority 4: add geometry-table conversion

The current individual geometry functions work.

The table workflow still needs batch geometry support:

```python
geometry_table_to_cells(...)
```

It should support:

- Point;
- MultiPoint;
- LineString;
- MultiLineString;
- Polygon; and
- MultiPolygon.

For each source feature, keep:

```text
source_id
gid
coverage_ratio or length_ratio
assignment_method
```

Do not mix this with final aggregation. Keep the contribution table auditable.

## Priority 5: geometry-aware aggregation

The current aggregation functions operate on already-assigned rows.

The next layer should combine:

```text
geometry table
  → cell contributions
  → value allocation
  → cell aggregation
```

The value meaning must be explicit:

```text
COUNT
TOTAL
DENSITY
MEASUREMENT
RATE
ORDINAL
CATEGORICAL
RANGE
```

Do not treat a polygon total, density, and average as the same value.

## 7. Release blockers and attention

## 7.1 Candidate profiles versus production profiles

All 11 domains are in the signed candidate registry.

Most custom ASEAN profiles use static WGS84-style projected candidates with:

```json
"reference_epoch": null
```

This means no dynamic datum transformation is available.

Before a production geodetic release, decide one of these:

1. approve the static candidate policy for this release;
2. replace each profile with a correct national datum CRS; or
3. label the PyPI release clearly as a technical candidate.

Do not hide this distinction.

## 7.2 Boundary data licensing

The code is Apache-2.0.

The boundary files have different source licenses, including ODbL, CC BY, CC BY-SA, and public domain.

Before public PyPI upload:

- review redistribution rights;
- keep the source attribution;
- add a clear `NOTICE` or attribution file;
- record which files are included in the wheel/sdist; and
- confirm that each license permits redistribution in the package.

The Apache license for the code does not replace the boundary data licenses.

## 7.3 Old private key history

The old private and public PEM paths are gone from the reachable branch history after the purge.

Still keep the new private key outside Git.

Run a secret scan before upload.

Do not upload any PEM private key.

## 7.4 Package size

Current artifacts are approximately:

```text
wheel: about 17 MB
sdist: about 33 MB
```

Most of the size comes from full boundary GeoJSON files.

Decide whether to:

- keep all full boundaries inside the PyPI package;
- ship only the signed registry and simplified metadata;
- make boundaries a separate data package; or
- provide a separate boundary download bundle.

If `verify_boundaries=True` is the normal user path, the required boundary files must still be available somewhere trusted.

## 7.5 Version naming

Current package version:

```text
0.1.0
```

Current profile version:

```text
2.0.0-rc.2-asean
```

Decide whether PyPI should publish:

```text
0.1.0rc1
```

for the current candidate, or:

```text
0.1.0
```

for a production release.

Recommended:

- use `0.1.0rc1` while profiles are still candidate/static;
- reserve `0.1.0` for the first approved production release.

## 7.6 Current boundary behavior to review

The boundary `INTERSECTS` implementation and the written wording must stay aligned.

If the intended rule is positive-area overlap, do not allow a point-only or line-only touch to pass.

Add explicit tests for:

- corner touch;
- edge touch;
- positive-area overlap;
- coastal cells; and
- multipolygon boundaries.

## 8. Exact next-session checklist

1. Review and commit the current dataset contract files.
2. Add root dataset docs/schema to the sdist/package strategy.
3. Implement `Manifest` parsing and validation.
4. Add Parquet metadata embedding.
5. Add `write_cell_dataset()` locally.
6. Add `read_cell_dataset()` locally.
7. Add compact and queryable dataset fixtures.
8. Add invalid-manifest tests.
9. Add invalid-GID and duplicate-GID tests.
10. Add an S3-compatible filesystem test.
11. Add geometry-table conversion.
12. Add geometry-aware aggregation.
13. Resolve boundary-license redistribution and add `NOTICE`.
14. Decide `0.1.0rc1` versus `0.1.0`.
15. Rebuild the wheel and sdist.
16. Run the 144-test suite again.
17. Run `twine check`.
18. Run a final secret scan.
19. Create a release tag.
20. Upload to TestPyPI first.
21. Install from TestPyPI in a clean environment.
22. Upload to PyPI only after the TestPyPI check passes.

## 9. PyPI release commands

After final approval:

```zsh
.venv/bin/python -m build
.venv/bin/twine check dist/*
.venv/bin/twine upload --repository testpypi dist/*
```

Test install:

```zsh
python3.11 -m venv /tmp/geosquare-pypi-test
/tmp/geosquare-pypi-test/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  geosquare-grid-v2
```

Then test:

```python
import geosquare_v2
```

Only after that:

```zsh
.venv/bin/twine upload dist/*
```

Do not upload with a private registry key in the package.

## 10. Final handover summary

The core GeoSquare V2 system is implemented and tested.

The all-ASEAN signed candidate registry is built and packaged.

The next important work is not another grid algorithm.

It is the data distribution layer:

```text
manifest
  → Parquet writer
  → S3 reader
  → validation
  → query
  → lazy geometry
  → aggregation
```

The main release attention points are:

1. static versus national-datum profile policy;
2. boundary license redistribution;
3. package size;
4. dataset manifest validation;
5. S3 read/write behavior;
6. clean PyPI installation; and
7. final secret and release authorization checks.
