# GeoSquare V2 documentation

GeoSquare V2 is a country-scoped hierarchical metric grid.

It gives locations stable square-grid addresses. It computes cell geometry when needed. It supports point indexing, geometry conversion, table data, aggregation, neighbours, distance, migration, and signed country profiles.

## Start here

1. [Overview](01_OVERVIEW.md)
2. [API guide](02_API.md)
3. [Data conversion and aggregation](03_DATA_AND_AGGREGATION.md)
4. [Boundaries and migration](04_BOUNDARIES_AND_MIGRATION.md)
5. [Country profiles](05_COUNTRY_PROFILES.md)
6. [Interoperability and comparisons](06_COMPARISON.md)
7. [Migration and release](07_RELEASE_AND_SECURITY.md)

## Source documents

These root documents contain the detailed technical rules:

- [Changelog](../CHANGELOG.md)
- [Product contract](../PRODUCT_CONTRACT_V2.md)
- [Technical specification](../V2SPECS.md)
- [Architecture decisions](../ARCHITECTURE_DECISIONS.md)
- [Core logic and CRS guide](../CRUCIAL_LOGIC.md)
- [Simple service API](../SERVICE_API.md)
- [Data-to-grid contract](../DATA_TO_GRID_CONTRACT.md)
- [Boundary policy](../BOUNDARY_POLICY.md)
- [V1 migration guide](../MIGRATION_V1_V2.md)
- [Release candidate guide](../RELEASE_CANDIDATE.md)
- [SQLite registry guide](../SQLITE_REGISTRY_GUIDE.md)

## Current status

The codebase is still a release candidate.

The core model is implemented. The signed candidate registry now contains all 11 ASEAN domains.

The candidate release has passed the pinned 144-test suite, clean wheel/sdist install checks, and verified 11-domain registry loading.

Before public production upload, still complete:

- final profile and static-epoch approval;
- boundary authority approval;
- Git-history cleanup for the old private key;
- release authorization; and
- PyPI upload review.

The current artifacts are ready as a release candidate. They are not uploaded by this agent.

## Public API names

Use these names in new code:

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

Older names remain as aliases for now:

```text
index_point  -> point_to_cell
polyfill     -> polygon_to_cells
neighbourhood -> cell_neighbours
distance     -> cell_distance
```

## Optional dependencies

```text
geo       PyProj and Shapely
registry  Ed25519, RFC 8785, and PROJ checks
batch     NumPy, Pandas, and Arrow encoders
table     Pandas, Arrow, and XLSX table input/output
analytics geo + batch
dev       Pytest and test helpers
```

Install the full development set with:

```zsh
python -m pip install -e ".[analytics,registry,table,dev]"
```

## Design rule

The canonical identity is always:

```text
(domain_code, level, x_idx, y_idx)
```

GID, packed IDs, and geometry are derived forms. Do not make a display label or a third-party index the canonical identity.
