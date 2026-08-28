# ID and VN Registry Release Candidate

This candidate defines two canonical V2 national domains:

| Domain | Canonical grid CRS | Reference zonal systems | Boundary source |
|---|---|---|---|
| `ID` | `GEOSQUARE:ID_SRGI2013_EQC_V2` — custom SRGI2013 Equidistant Cylindrical centred at 118°E | SRGI2013 UTM/TM zones are reference/ingestion metadata only, never alternate canonical GID roots. | geoBoundaries gbOpen IDN ADM0, 2017, ODbL |
| `VN` | `GEOSQUARE:VN_VN2000_LCC_V2` — custom VN-2000 Lambert Conformal Conic centred at 107.5°E with 11°N/21°N standard parallels | VN-2000 UTM/TM zones are reference/ingestion metadata only, never alternate canonical GID roots. | geoBoundaries gbOpen VNM ADM0, 2016, CC BY 4.0 |

`registry.unsigned.v2.json` is intentionally not loadable. Review all generated profiles, boundary hashes, CRS definitions, and scale metadata; then sign it locally:

```zsh
.venv/bin/python scripts/sign_registry.py \
  --private-key /secure/path/geosquare-registry-private.pem \
  --input src/geosquare_v2/data/registry/registry.unsigned.v2.json \
  --output src/geosquare_v2/data/registry/registry.v2.json \
  --key-id geosquare-registry-2026-08
```

The loader receives the public trust anchor from `registry-trust.json` (or preferably a separately distributed application trust store). Never commit or attach the private key.

Before changing any generated artifact, re-run:

```zsh
.venv/bin/python scripts/generate_release_candidates.py
```

Then review the resulting diff and sign the new unsigned manifest. The profile generator pins exact artifact bytes and the local PROJ database/version; an upgrade to PROJ requires a fresh candidate generation and signature.

Boundary attribution and source details are in `src/geosquare_v2/data/registry/boundaries/SOURCES.md`.
