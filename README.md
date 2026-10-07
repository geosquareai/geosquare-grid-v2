# GeoSquare Grid V2

Need stable cell IDs for points, lines, or polygons?

GeoSquare Grid V2 turns geographic data into shared square cells. It gives you IDs that work across files, databases, APIs, and countries.

The main Python import is:

```python
import geosquare_v2
```

> **Current status: `0.1.0rc1` technical candidate.** This local candidate is not production geodetic data and has not been uploaded to TestPyPI or PyPI. The ASEAN profiles are signed release candidates, not final production profiles. Boundary attribution and redistribution notes are in [NOTICE](NOTICE); the approval gates remain open.

## What can I do with it?

Most users come here with one of these problems:

1. “I have points. How do I put them into stable cells?”
2. “My polygons cross many cells. How do I keep the split visible?”
3. “How do I add values without mixing totals, densities, and averages?”
4. “How do I read only the cells in a map viewport?”
5. “How do I save the result locally or in S3?”

The examples below focus on those jobs.

## Install from the repository

PyPI publication is still pending. For now, install from a local checkout:

```zsh
# Point and registry workflows
python -m pip install -e ".[registry]"

# Geometry, tables, Arrow, and aggregation
python -m pip install -e ".[analytics,registry,table]"

# Optional fsspec and S3-style storage
python -m pip install -e ".[analytics,registry,table,filesystem]"
# Use .[... ,s3] when you need the real s3fs backend.
```

Python 3.11 or newer is required.

## First, load a trusted registry

The registry tells GeoSquare which profile belongs to each domain. It also verifies the signed candidate database.

```python
import base64
import json
from pathlib import Path

from geosquare_v2 import DbRegistryLoader, GeosquareService

root = Path(".")
keys = json.loads((root / "registry-trust.json").read_text())
trust = {
    key_id: base64.b64decode(value, validate=True)
    for key_id, value in keys.items()
}

registry = DbRegistryLoader(
    trust,
    root / "src/geosquare_v2/db",
    boundary_root=root / "src/geosquare_v2/data/registry",
    verify_boundaries=True,
).load()

service = GeosquareService(
    registry,
    boundary_root=root / "src/geosquare_v2/data/registry",
)
```

In an installed application, point the loader to your packaged registry and your trusted public-key store. Never put a private signing key in the repository or package.

## Use case 1: put points into cells

### The problem

You have a CSV, DataFrame, or Parquet file with longitude and latitude. You need a stable cell ID for each row.

### The solution

```python
assigned = service.table_to_cells(
    "points.parquet",
    "ID",
    level=12,
    longitude_column="longitude",
    latitude_column="latitude",
    keep_columns=["asset_id", "value"],
)
```

The output keeps your selected fields and adds:

```text
domain
level
x_idx
y_idx
gid
uri
packed_id
```

The durable URI looks like this:

```text
geosquare:v2:ID:<gid>
```

Store the URI when you need an identifier that includes both the grid version and domain.

For a single point:

```python
cell = service.point_to_cell(
    "ID",
    longitude=106.8456,
    latitude=-6.2088,
    level=12,
)

print(cell.uri)
print(cell.projected_bounds)
print(cell.cell_edge_m)
```

## Use case 2: split polygons and lines into contributions

### The problem

A polygon or line can cross many cells. One final row per cell hides how the value was assigned.

### The solution

Create an auditable contribution table first:

```python
from geosquare_v2 import geometry_table_to_cells

contributions = geometry_table_to_cells(
    "parcels.parquet",
    service,
    "ID",
    level=12,
    geometry_column="geometry",
    source_id_column="parcel_id",
    source_crs="EPSG:4326",
    keep_columns=["population"],
)
```

A contribution table keeps fields such as:

```text
source_id
source payload fields
domain
level
gid
uri
coverage_ratio
length_ratio
assignment_method
boundary_policy
```

Use `coverage_ratio` for polygon shares. Use `length_ratio` for line shares. A source feature can create several rows.

For polygon totals, the table normalizes the coverage shares for each source feature. The shares add up to one before allocation.

Boundary filtering is always explicit:

```python
from geosquare_v2 import BoundaryPredicate

contributions = geometry_table_to_cells(
    "parcels.parquet",
    service,
    "ID",
    level=12,
    geometry_column="geometry",
    source_id_column="parcel_id",
    source_crs="EPSG:4326",
    boundary_policy=BoundaryPredicate.INTERSECTS,
)
```

Available policies are:

```text
COVERS_POINT
CENTROID_COVERED
INTERSECTS
MIN_COVERAGE
```

## Use case 3: aggregate values without losing their meaning

### The problem

A polygon total is not a density. A rate is not a sum. A category is not an average.

### The solution

Tell GeoSquare what the value means:

```python
from geosquare_v2 import aggregate_geometry_table_to_cells

population_by_cell = aggregate_geometry_table_to_cells(
    "parcels.parquet",
    service,
    "ID",
    level=12,
    value_semantics="TOTAL",
    value_column="population",
    geometry_options={
        "geometry_column": "geometry",
        "source_id_column": "parcel_id",
        "source_crs": "EPSG:4326",
        "keep_columns": ["population"],
    },
)
```

Supported meanings are:

| Meaning | Default behavior |
|---|---|
| `COUNT` | Count contribution rows. |
| `TOTAL` | Allocate by normalized area or length share, then sum. |
| `DENSITY` | Return a ratio-weighted mean. Keep it as a density. |
| `MEASUREMENT` | Return a ratio-weighted mean. |
| `RATE` | Aggregate numerator/denominator columns, or use a weighted mean. |
| `ORDINAL` | Use an explicit priority order. |
| `CATEGORICAL` | Use an explicit category rule. |
| `RANGE` | Use an explicit range rule. |

For an existing contribution table:

```python
from geosquare_v2 import aggregate_geometry_contributions

result = aggregate_geometry_contributions(
    contributions,
    value_semantics="TOTAL",
    value_column="population",
)
```

The selected meaning and allocation rule are recorded in:

```python
result.attrs["geosquare"]
```

This makes the result easier to audit. It also stops a later user from guessing what the number means.

## Use case 4: query cells in a map viewport

### The problem

A map only needs the cells inside its current viewport. Loading every cell wastes time and memory.

### The solution

Write a queryable dataset with `packed_id`, `x_idx`, and `y_idx`, then query it:

```python
from geosquare_v2 import query_cell_dataset

visible = query_cell_dataset(
    "datasets/population/",
    bbox=(106.7, -6.3, 106.9, -6.1),
    domain="ID",
    level=12,
    registry=registry,
)
```

The local query path uses Parquet predicate filtering on the x/y index. It does not build every cell geometry.

The bbox uses WGS84 longitude and latitude:

```text
(min_lon, min_lat, max_lon, max_lat)
```

Antimeridian-crossing bboxes are supported. GID-only compact datasets are not queryable by rectangular window.

## Use case 5: save and read a cell dataset

### The problem

You need a portable dataset with enough metadata to explain what each GID means.

### The solution

A dataset contains:

```text
dataset/
├── manifest.json
└── data/
    └── part-00000.parquet
```

The manifest records the domain, level, profile version, value semantics, aggregation rule, coverage policy, source, and provenance.

After creating a validated Arrow table and manifest:

```python
from geosquare_v2 import CellDataset

dataset = CellDataset.from_table(
    arrow_table,
    manifest,
    registry=registry,
)
dataset.write("datasets/population/")
```

Read it later:

```python
from geosquare_v2 import read_cell_dataset

loaded = read_cell_dataset(
    "datasets/population/",
    registry=registry,
)
```

The reader checks:

- the sidecar manifest;
- embedded Parquet metadata;
- Arrow column types;
- row counts;
- GIDs;
- packed and x/y identity fields;
- duplicate rules; and
- coverage or length ratios.

A `cell_values` dataset has one row per unique GID. A `cell_contributions` dataset may repeat GIDs.

See [CELL_DATASET_CONTRACT.md](CELL_DATASET_CONTRACT.md) for the full manifest and column rules.

## Use case 6: read or write through S3-style storage

### The problem

Your data lives in object storage, but you do not want a second data format.

### The solution

Install the optional filesystem extra:

```zsh
python -m pip install -e ".[analytics,registry,table,filesystem]"
```

Then use the same dataset layout through fsspec:

```python
from geosquare_v2 import (
    read_cell_dataset_filesystem,
    write_cell_dataset_filesystem,
)

write_cell_dataset_filesystem(
    dataset,
    "s3://my-bucket/datasets/population/",
)

loaded = read_cell_dataset_filesystem(
    "s3://my-bucket/datasets/population/",
    registry=registry,
)
```

For a real S3 filesystem, install the `s3` extra. The base package does not install `boto3`, `fsspec`, or `s3fs`.

You can also query through the filesystem backend:

```python
from geosquare_v2 import query_cell_dataset_filesystem

visible = query_cell_dataset_filesystem(
    "s3://my-bucket/datasets/population/",
    bbox=(106.7, -6.3, 106.9, -6.1),
    registry=registry,
)
```

Local queries use Parquet predicate pushdown. Filesystem-backed queries keep the same validation and result behavior through Arrow filtering.

## Choosing a cell level

Levels use the same hierarchy everywhere. The grid alternates 5x5 and 2x2 subdivisions.

Common reference points:

- level 9: about 1 km cells;
- level 12: about 50 m cells;
- level 14: about 5 m cells.

The exact size is defined in each profile’s grid CRS. Choose the level from your use case:

- use a coarser level for regional summaries;
- use level 9 for many city-scale analyses;
- use level 12 or finer for detailed local work.

## Important things to know

### Profiles are candidates

The repository contains 11 ASEAN candidate domains. Some use static WGS84-style projected candidates. They are not final national-datum production profiles.

### Boundaries do not change cell IDs

A boundary policy only decides whether an application keeps a cell or contribution. It does not change the cell ID.

### Do not use GID text for spatial ranges

Use these fields for spatial filtering:

```text
domain
level
x_idx
y_idx
```

A GID is an identifier. Its text order is not a geographic sort order.

### Version your durable IDs

Do not store only a bare GID in long-lived data. Prefer:

```text
geosquare:v2:<domain>:<gid>
```

## Common API names

```python
from geosquare_v2 import (
    CellDataset,
    aggregate_geometry_contributions,
    aggregate_geometry_table_to_cells,
    geometry_table_to_cells,
    query_cell_dataset,
    read_cell_dataset,
    write_cell_dataset,
)
```

Older names remain available for compatibility in parts of the API. New code should use the names above.

## Development checks

From the repository root:

```zsh
.venv/bin/python -B -m pytest -q
.venv/bin/python -m pip check
```

The current test suite covers the grid, registry, geometry conversion, dataset manifests, local Parquet storage, viewport queries, geometry aggregation, and optional filesystem backends.

## Documentation

- [Complete documentation](docs/README.md)
- [API guide](docs/02_API.md)
- [Data and aggregation guide](docs/03_DATA_AND_AGGREGATION.md)
- [Cell dataset contract](CELL_DATASET_CONTRACT.md)
- [Boundary policy](BOUNDARY_POLICY.md)
- [V1 to V2 migration guide](MIGRATION_V1_V2.md)
- [Candidate release notes](RELEASE_CANDIDATE.md)
- [Handover and next steps](HANDOVER.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)

## License and data sources

The code is Apache-2.0 licensed.

Boundary files have their own source licenses and attribution requirements. See:

```text
src/geosquare_v2/data/registry/boundaries/SOURCES.md
```

Review those terms before redistributing the package or boundary data.
