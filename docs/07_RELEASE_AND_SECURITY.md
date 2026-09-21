# Release and security guide

## 1. Current release state

The project is a release candidate.

The signed SQLite registry is distributed at:

```text
src/geosquare_v2/db/registry.db
src/geosquare_v2/db/registry.db.sig
```

The current signed candidate contains all 11 ASEAN domains. The profiles are still release candidates until datum, boundary, epoch, and production approval gates pass.

## 2. Release artifacts

A release contains:

- package source;
- signed registry database;
- detached database signature;
- trusted public key material;
- profile metadata;
- boundary files;
- boundary source notes;
- scale reports; and
- reproducible build information.

The database and signature are a pair. Change one and regenerate the other.

## 3. Signing keys

The private Ed25519 key must:

- stay outside the Git repository;
- stay outside distributed packages;
- have restricted file permissions;
- be kept offline or in a secure signing service; and
- never be pasted into chat or committed.

The public key is not secret.

Applications use a trusted public key to verify the detached signature.

The signing scripts reject private-key paths inside the repository.

## 4. Registry verification

A verified loader checks:

1. the database signature;
2. the SHA-256 digest of the database;
3. registry structure;
4. domain/profile identity;
5. profile hashes;
6. scale metadata hashes;
7. boundary hashes when enabled;
8. CRS parseability;
9. exact PROJ version; and
10. PROJ database/resource hashes.

A local PROJ mismatch is not a reason to bypass verification. Use the pinned environment.

## 5. Generate a candidate database

Generate from reviewed source artifacts:

```zsh
python scripts/generate_release_candidates.py
```

Inspect:

- profiles;
- boundary sources;
- scale reports;
- CRS WKT2;
- domain IDs;
- registry rows; and
- generated diffs.

## 6. Sign the database

Use a private key outside the repository:

```zsh
python scripts/sign_registry_db.py \
  --private-key /secure/location/geosquare-registry-private.pem \
  --db src/geosquare_v2/db/registry.db \
  --output src/geosquare_v2/db/registry.db.sig \
  --key-id geosquare-registry-YYYY-MM
```

Update the trusted public key in the application trust store.

Do not put the private key in the project repository.

## 7. Package data

`pyproject.toml` includes:

```text
src/geosquare_v2/db/*.db
src/geosquare_v2/db/*.sig
src/geosquare_v2/data/registry/boundaries/*.geojson
src/geosquare_v2/data/registry/boundaries/*.json
src/geosquare_v2/data/registry/boundaries/*.md
```

Build both a wheel and an sdist.

Install them in a clean environment.

Load the signed registry from the installed package.

## 8. Release gates

Do not publish until:

- no private key is in Git;
- the clean package contains the database and signature;
- the trusted public key verifies the signature;
- the pinned PROJ environment passes;
- scalar conformance tests pass;
- geometry and boundary tests pass;
- batch outputs match scalar outputs;
- table and aggregation tests pass;
- migration fixtures pass;
- country profiles pass approval; and
- the release is reviewed by a human.

## 9. Validation commands

```zsh
python -m compileall -q src scripts tests
python -m pytest -q -W error::DeprecationWarning
python -m pip check
```

Also run:

```zsh
python scripts/benchmark_asean_profiles.py
python scripts/benchmark_cross_system_asean.py
```

## 10. Do not edit signed artifacts by hand

Do not edit:

- `registry.db`;
- `registry.db.sig`;
- signed profiles; or
- trusted release metadata.

Change the source artifact. Regenerate the database. Review it. Sign it again.
