# ASEAN V2 registry release candidate

**Status:** candidate, not production
**Profile version:** `2.0.0-rc.2-asean`

This candidate contains all 11 ASEAN country domains.

| Domain ID | Code | Country | Projection candidate | Boundary |
|---:|---|---|---|---|
| 1 | `ID` | Indonesia | LCC 1/6 candidate | full |
| 2 | `VN` | Viet Nam | existing VN-2000 LCC | full |
| 3 | `BN` | Brunei Darussalam | LCC | full |
| 4 | `KH` | Cambodia | LCC | full |
| 5 | `LA` | Lao PDR | LCC | full |
| 6 | `MY` | Malaysia | LCC 1/6 candidate | full |
| 7 | `MM` | Myanmar | LCC 1/6 candidate | full |
| 8 | `PH` | Philippines | LCC 1/6 candidate | full |
| 9 | `SG` | Singapore | local projected candidate | full |
| 10 | `TH` | Thailand | LCC 1/6 candidate | full |
| 11 | `TL` | Timor-Leste | LCC | full |

The source boundary metadata and hashes are in:

```text
boundaries/SOURCES.md
src/geosquare_v2/data/registry/boundaries/SOURCES.md
boundaries/ASEAN_BOUNDARY_METADATA.json
```

## Important candidate limits

This is a signed candidate registry.

It is not yet a legal or production boundary release.

The custom candidate profiles use static WGS84-style CRS definitions where an approved national datum has not yet been added. Those profiles have no dynamic coordinate epoch. That policy must be reviewed before a production geodetic release.

The profile review files are:

```text
ASEAN_PRIORITY_PROFILE_REVIEW.md
ASEAN_PRIORITY_PROFILE_REVIEW.json
profiles/ASEAN_PRIORITY_PROFILE_DECISIONS.json
ASEAN_SQUARENESS_BENCHMARK.md
```

## Generate the registry

Use the ASEAN generator:

```zsh
.venv/bin/python scripts/generate_asean_release_candidates.py
```

It writes:

```text
profiles/*.v2.json
scale/*_GRID_V2.json
registry.v2.json
src/geosquare_v2/db/registry.db
```

The database is unsigned until the review is complete.

## Sign the registry

Keep the private key outside the repository:

```zsh
.venv/bin/python scripts/sign_registry_db.py \
  --private-key /secure/path/geosquare-registry-private.pem \
  --db src/geosquare_v2/db/registry.db \
  --output src/geosquare_v2/db/registry.db.sig \
  --key-id geosquare-registry-YYYY-MM
```

Then update the trusted public key in the application trust store.

Never commit or distribute the private key.

## Verify the candidate

```zsh
.venv/bin/python - <<'PY'
import base64
import json
from pathlib import Path
from geosquare_v2.db import DbRegistryLoader

root = Path('.')
keys = json.loads((root / 'registry-trust.json').read_text())
trust = {key: base64.b64decode(value) for key, value in keys.items()}
registry = DbRegistryLoader(
    trust,
    root / 'src/geosquare_v2/db',
    boundary_root=root / 'src/geosquare_v2/data/registry',
    verify_boundaries=True,
).load()
print(len(registry), [profile.domain_code for profile in registry.profiles()])
PY
```

Expected domains:

```text
BN KH ID LA MM MY PH SG TH TL VN
```

## Package validation

Build both package formats:

```zsh
.venv/bin/python -m build
```

The wheel and sdist must contain:

- the V2 Python package;
- `registry.db`;
- `registry.db.sig`;
- all full boundary files;
- boundary metadata; and
- package metadata.

Install each artifact into a clean Python 3.11+ environment. Load the registry again.

## Final approval before production

Before changing the status from candidate to production:

1. approve the national datum policy for every domain;
2. review the boundary authority and license;
3. review the profile scale report;
4. review island and component behavior;
5. review the static epoch policy;
6. run the full pinned test suite;
7. build and test wheel and sdist;
8. verify the signature with an external trust store;
9. remove the old private key from Git history; and
10. obtain release authorization.
