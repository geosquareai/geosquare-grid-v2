# GeoSquare Grid V2 handover

- **Original handover date:** 2026-09-18
- **Last baseline verification:** 2026-10-01
- **Repository:** `geosquare-grid-v2`
- **Package name:** `geosquare-grid-v2`
- **Python import:** `geosquare_v2`
- **Current package metadata/artifacts:** candidate target `0.1.0rc1`; tracked `dist/` artifacts remain historical `0.1.0` inputs and must not be reused
- **Release target:** `0.1.0rc1` technical candidate
- **Current profile version:** `2.0.0-rc.2-asean`
- **Publication status:** Not uploaded to TestPyPI or PyPI

This document explains the current state, the important decisions, the remaining work, and the main things to watch before publishing. The baseline below was verified on 2026-10-01.

## 1. Current Git state

Baseline verified on 2026-10-01:

```text
db_registry        7db4c6c  origin/db_registry
main               5b98c6d  origin/main
origin/HEAD        origin/main
```

The current `db_registry` commit is:

```text
7db4c6c new handover doc
```

The `main` release commit remains:

```text
5b98c6d Prepare ASEAN V2 release candidate
```

The old signing PEM paths were not present in reachable history during the Phase 0 scan:

```text
geosquare-registry-private.pem
geosquare-registry-public.pem
```

The old private key must still be considered compromised. Do not reuse it.

The new private key is outside the repository. It must stay there and must never be committed or distributed.

No PEM paths were found in reachable Git history, and no sensitive PEM/private/secret filenames were found in the existing wheel or sdist. This does not replace the required final secret scan before release.

## 2. Current working-tree and artifact state

At the start of Phase 0 verification, the only working-tree change was:

```text
?? IMPLEMENTATION_PLAN.md
```

`IMPLEMENTATION_PLAN.md` and this handover update are documentation changes created during the current planning session and remain intentionally uncommitted until reviewed.

The following files are already tracked and unchanged, despite the older handover describing them as uncommitted:

```text
CELL_DATASET_CONTRACT.md
schemas/cell-dataset-manifest-v1.schema.json
README.md
DATA_TO_GRID_CONTRACT.md
docs/README.md
docs/03_DATA_AND_AGGREGATION.md
```

The following are also tracked in the current branch and unchanged:

```text
.DS_Store
dist/geosquare_grid_v2-0.1.0-py3-none-any.whl
dist/geosquare_grid_v2-0.1.0.tar.gz
```

They should not be regenerated or added to future release commits unless explicitly intended. Cleanup of tracked build artifacts and `.DS_Store` is a separate repository-hygiene decision and is not part of Phase 0.

The tracked wheel and sdist remain historical package metadata for version `0.1.0`. Candidate artifacts must be built fresh under `dist-candidate/`; they must not be reused, overwritten, or uploaded as the `0.1.0rc1` candidate.

The dataset contract work is the next development step. Implement and test the local manifest and Parquet layer before adding S3 support.

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

The Phase 0 baseline suite passed:

```text
.venv/bin/python -m pytest -q
144 passed in 4.34s
```

The Phase 1 suite passed after manifest implementation:

```text
.venv/bin/python -B -m pytest -q
162 passed in 2.42s
```

Public import and source/package schema consistency checks passed. Temporary wheel and sdist builds both included:

```text
geosquare_v2/data/cell-dataset-manifest-v1.schema.json
```

Dependency verification also passed:

```text
.venv/bin/python -m pip check
No broken requirements found.
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

The wheel and sdist contain the package, registry, signature, full boundaries,
metadata, and documentation included by `MANIFEST.in`. The current full suite
collects 195 tests. The earlier 144-test and 162-test results above are
historical phase checkpoints, not the current release-hardening result.
Candidate validation must use fresh artifacts in `dist-candidate/`, while
tracked `dist/` and `.DS_Store` files remain untouched.

## 6. Highest-priority next work

## Priority 1: finish the cell dataset format

The current contract files are:

```text
CELL_DATASET_CONTRACT.md
schemas/cell-dataset-manifest-v1.schema.json
```

Phase 1 is complete for the manifest contract. The implementation now includes:

- `CellDatasetManifest` parsing and deterministic JSON serialization;
- standard-library structural and cross-field validation;
- trusted domain, profile-version, and boundary-hash checks;
- declared-column validation for compact, queryable, and contribution datasets;
- the dedicated `CellDatasetManifestError`; and
- 18 focused valid/invalid manifest tests.

The manifest contract and local Parquet storage are complete. The next implementation step is query support over queryable datasets. S3 remains deferred until query and local validation behavior are stable.

Next implementation steps:

1. Implement the `CellDataset` object around a PyArrow table/dataset.
2. Validate the Parquet schema against the manifest.
3. Validate GIDs, identity columns, duplicate rules, coverage ratios, and row counts.
4. Embed the manifest in Parquet metadata.
5. Write and verify a sidecar `manifest.json`.
6. Add compact and queryable local Parquet round-trip tests.
7. Add a clean example dataset.

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

The runtime schema is now packaged at:

```text
src/geosquare_v2/data/cell-dataset-manifest-v1.schema.json
```

`pyproject.toml` includes it in `tool.setuptools.package-data`, and the source schema remains at `schemas/cell-dataset-manifest-v1.schema.json` for review and documentation. The temporary Phase 1 wheel build confirmed that the packaged schema is included. The root Markdown contract remains documentation and is not required for runtime manifest validation.

## Priority 2: implement `CellDataset`

### Status: complete for local storage

The local PyArrow-backed `CellDataset` is implemented in:

```text
src/geosquare_v2/dataset.py
```

The supported local API is:

```python
dataset = CellDataset.from_table(table, manifest, registry=registry)
dataset.write("path/to/dataset/")

dataset = read_cell_dataset("path/to/dataset/", registry=registry)
dataset.validate()
```

The local format uses:

```text
dataset/
├── manifest.json
└── data/
    └── part-00000.parquet
```

The writer embeds the canonical manifest under `geosquare.manifest` and refuses to overwrite an existing destination. The reader validates sidecar/embedded metadata, Arrow types, row counts, GIDs, identity columns, duplicate policy, provenance, and ratio bounds.

Remote filesystems, S3, lazy scanning, query pushdown, geometry construction, and aggregation remain future work. Keep S3 support optional; do not add `boto3` to the core package without a clear need.

## Priority 3: add dataset query support

### Status: complete for local queryable datasets

The public API is:

```python
query_cell_dataset(
    "path/to/dataset/",
    bbox=(min_lon, min_lat, max_lon, max_lat),
    domain="ID",
    level=12,
    registry=trusted_registry,
)
```

The local query layer:

- reads and validates the sidecar and embedded manifests first;
- requires a trusted `DomainRegistry` and matching domain/level;
- requires `packed_id`, `x_idx`, and `y_idx` query metadata;
- validates WGS84 bbox coordinates;
- supports antimeridian-crossing bboxes;
- transforms bbox corners with an `always_xy` profile CRS transformer;
- calculates clamped x/y candidate windows;
- uses `pyarrow.dataset` predicate filtering;
- returns a schema-preserving PyArrow table; and
- rejects compact GID-only datasets.

Five focused query tests cover valid filtering, metadata preservation, mismatch errors, compact datasets, invalid bboxes, empty results, and antimeridian splitting. S3 and remote filesystem query support remain deferred.

## Priority 4: add geometry-table conversion

### Status: complete

The public API is:

```python
geometry_table_to_cells(
    source,
    service,
    domain_code,
    level,
    geometry_column="geometry",
    source_id_column="asset_id",
    source_crs="EPSG:4326",
)
```

The converter supports:

- Point;
- MultiPoint;
- LineString;
- MultiLineString;
- Polygon; and
- MultiPolygon.

Each contribution preserves source payload fields, `source_id` or `source_row`, domain, level, GID, URI, nullable coverage/length ratios, assignment method, and boundary policy. It supports projected or WGS84 point inputs and explicit `OperationalBoundary` policies. It does not perform value allocation or final aggregation.

`boundary_policy` is now a reserved contribution column in the dataset contract and schema. Six focused tests pass, including validation of the generated table through `CellDataset` as a `cell_contributions` dataset.

## Priority 5: geometry-aware aggregation

### Status: complete

The public APIs are:

```python
aggregate_geometry_contributions(
    contributions,
    value_semantics="TOTAL",
    value_column="population",
)

aggregate_geometry_table_to_cells(
    source,
    service,
    domain_code,
    level,
    value_semantics="TOTAL",
    value_column="population",
    geometry_options={...},
)
```

Implemented semantics:

- `COUNT`: unit count per contribution row;
- `TOTAL`: normalized coverage/length ratio allocation followed by sum;
- `DENSITY`: ratio-weighted mean that remains a density;
- `MEASUREMENT`: ratio-weighted mean;
- `RATE`: weighted numerator/denominator aggregation or explicit weighted mean fallback;
- `ORDINAL`: priority-order aggregation;
- `CATEGORICAL`: explicit category rules; and
- `RANGE`: explicit range rules.

Results preserve allocation and semantic provenance in `DataFrame.attrs["geosquare"]`. Polygon contribution shares are normalized per source geometry so totals are conserved. Six focused aggregation tests pass, including the high-level geometry conversion pipeline and invalid rule handling.

The next work is optional filesystem/S3 support. Do not add `boto3` to core dependencies without a clear need.

## Priority 6: optional filesystem and S3 support

### Status: complete

The fsspec-backed APIs are:

```python
write_cell_dataset_filesystem(dataset, "memory://bucket/path/")
read_cell_dataset_filesystem("s3://bucket/path/", filesystem=fs)
query_cell_dataset_filesystem(
    "memory://bucket/path/",
    bbox=(min_lon, min_lat, max_lon, max_lat),
    registry=trusted_registry,
)
```

The base package remains filesystem-independent. Optional extras are pinned as:

```toml
filesystem = ["fsspec==2025.7.0"]
s3 = ["fsspec==2025.7.0", "s3fs==2025.7.0"]
```

The same manifest and Parquet layout is used for local, memory, and S3-style URLs. The test suite uses an injected in-memory fsspec filesystem for S3-compatible coverage and does not require live AWS credentials. Local queries retain predicate pushdown; filesystem queries preserve validation and result semantics through Arrow table filtering.

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

The code is Apache-2.0. The included boundary files have separate recorded
source licenses. The evidence-backed attribution for every metadata full and
simplified candidate file is in [NOTICE](NOTICE) and the mirrored
`src/geosquare_v2/data/registry/boundaries/SOURCES.md`.

The redistribution/license approval gate remains open for every boundary file.
The notice records source evidence only; it does not invent permission or
replace review of the applicable source terms. The full and simplified
boundaries remain in the candidate package because the signed registry and the
`verify_boundaries=True` path reference them.

## 7.3 Old private key history

The old private key is compromised and must never be reused. The historical
reachable-history scan reported no old PEM path, but that does not establish
that the key is safe. The new private key stays outside Git and all artifacts.
The final fail-closed scan covers source, release inputs, and both candidate
archives. Do not include any PEM private key.

## 7.4 Package size

The tracked historical artifacts are 17,440,667 bytes for the wheel and
34,580,131 bytes for the sdist. The fresh candidate sizes must be recorded in
`dist-candidate/` evidence. Most of the size comes from full boundary GeoJSON
files.

Package-size approval remains an explicit blocker while retaining full
boundaries. No boundary split, deletion, or alternative distribution strategy
is introduced during this candidate preparation.

## 7.5 Version naming

The package metadata now targets:

```text
0.1.0rc1
```

The tracked `dist/` artifacts remain historical `0.1.0` files and must not be
reused. The current profile remains:

```text
2.0.0-rc.2-asean
```

Reserve `0.1.0` for the first approved production release. The candidate/static
profile status and the unresolved boundary redistribution and package-size
decisions require this release to remain clearly labelled as a technical
candidate.

## 7.6 Current boundary behavior to review

The boundary `INTERSECTS` implementation and the written wording must stay aligned.

If the intended rule is positive-area overlap, do not allow a point-only or line-only touch to pass.

Add explicit tests for:

- corner touch;
- edge touch;
- positive-area overlap;
- coastal cells; and
- multipolygon boundaries.

## 8. Exact release-hardening checklist

1. Review the evidence-backed [NOTICE](NOTICE) and keep redistribution approval
   open until a human confirms the source terms.
2. Keep the static/candidate geodetic status explicit and obtain approval for
   distributing `0.1.0rc1` as a technical candidate, not production data.
3. Obtain package-size approval while retaining full boundaries.
4. Run the fail-closed secret scan across source, release inputs, and both
   candidate archives.
5. Build fresh wheel and sdist artifacts under `dist-candidate/`.
6. Inspect both archives and record metadata, package data, registry,
   signature, schema, boundaries, and byte sizes.
7. Run `twine check`, `pip check`, the 195-test suite, compile checks, and
   clean wheel/sdist installs.
8. Record all results in `.agents/tasks/evidence.md`.
9. Stop at the local no-upload gate. Preserve tracked `dist/` and `.DS_Store`
   files; do not commit, tag, push, or contact TestPyPI/PyPI.

## 9. Local candidate validation commands

```zsh
.venv/bin/python -m build --sdist --wheel --outdir dist-candidate
.venv/bin/twine check dist-candidate/*
.venv/bin/python -m pip check
.venv/bin/python -B -m pytest -q
```

Use clean temporary environments with direct local references to the two
`dist-candidate/` artifacts. The test must load the installed registry using
trusted public-key bytes supplied from the repository trust input and must
exercise one public point-to-cell call. No upload command is part of this
handover.

## 10. Final handover summary

The core GeoSquare V2 system is implemented and tested.

The all-ASEAN signed candidate registry is built and packaged.

The next important work is not another grid algorithm.

It is the data distribution layer:

```text
manifest
  → Parquet writer
  → validation
  → local query
  → optional S3 reader
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

## 11. Release-hardening evidence

The `0.1.0rc1` candidate was prepared locally only. No TestPyPI/PyPI upload,
commit, tag, push, or Git-history change occurred. The tracked `dist/` artifacts
and tracked `.DS_Store` files were preserved.

Candidate artifacts in the isolated directory:

```text
dist-candidate/geosquare_grid_v2-0.1.0rc1-py3-none-any.whl
dist-candidate/geosquare_grid_v2-0.1.0rc1.tar.gz
```

Exact byte sizes and SHA-256 hashes are recorded in
`.agents/tasks/evidence.md`.

Validation completed:

- `twine check dist-candidate/*`: both artifacts PASSED;
- `.venv/bin/python -m pip check`: `No broken requirements found.`;
- `.venv/bin/python -m compileall -q src scripts tests`: passed;
- `.venv/bin/python -B -m pytest -q`: `195 passed in 2.42s`;
- archive inspection: wheel 59 members and sdist 179 members; both contain
  `0.1.0rc1` metadata, Python `>=3.11`, registry database/signature, runtime
  schema, `NOTICE`, and all recorded boundary files with matching SHA-256;
- fail-closed scan: 257 source/release-input files plus all 59 wheel and 179
  sdist members scanned for suspicious filenames, PEM/private-key material,
  and credential assignments; no matches;
- clean wheel and sdist environments: `pip check` passed, installed version
  was `0.1.0rc1`, the 11-domain registry verified with installed boundaries,
  packaged schema/resources were present, and the ID level-9 point smoke call
  returned `geosquare:v2:ID:H2X545V39`.

Open blockers remain: human approval of boundary redistribution and `NOTICE`
accuracy, human approval to distribute the static/candidate geodetic profiles
as a technical candidate, and package-size approval while retaining full
boundaries. Full details are recorded in `.agents/tasks/evidence.md`.
