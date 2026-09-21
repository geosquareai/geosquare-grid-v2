# Changelog

## 0.1.0 — ASEAN V2 release candidate

Status: candidate. Not yet uploaded to PyPI.

### Added

- 11 ASEAN country domains in the signed candidate registry;
- projected square geometry computed on read;
- alternating 5x5 and 2x2 hierarchy;
- GID and packed signed Int64 codecs;
- parent, children, neighbours, rings, disks, and same-level distance;
- boundary policies for points, cells, polyfill, and neighbourhoods;
- point, polygon, and line to cell conversion;
- optional cell geometry output;
- CSV, XLSX, Parquet, and Pandas table input;
- selected source-field retention;
- numeric, categorical, ordinal, and range aggregation;
- V1 point and area migration adapter;
- signed SQLite registry loading;
- full ASEAN boundary metadata and source attribution;
- profile and cross-system benchmarks; and
- complete Markdown documentation.

### Release notes

- Country profiles are release candidates.
- Custom WGS84-style candidate profiles use a static/no-dynamic-epoch policy until national datum approval is complete.
- The registry is signed with an Ed25519 key stored outside the repository.
- The project has passed the pinned 144-test suite.
- Wheel and sdist installation checks passed.
