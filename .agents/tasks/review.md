# GeoSquare Grid V2 0.1.0rc1 release hardening and isolated candidate preparation

The release-hardening work changes the package and runtime version to `0.1.0rc1`, adds source-backed boundary attribution, and explicitly packages `NOTICE` and the runtime schema. It creates fresh wheel and sdist artifacts in `dist-candidate/` while preserving the tracked historical `0.1.0` artifacts and `.DS_Store` inputs. The candidate documentation keeps the signed registry and static/candidate profiles clearly non-production, and the evidence records passing archive, dependency, test, install, and secret-scan checks without a commit or upload. Watch for: **confirmed** boundary redistribution and `NOTICE` approval, static/candidate geodetic approval, and package-size approval remain publication gates; they are documented external blockers, not unresolved defects in the local candidate preparation.

**Verdict**: APPROVED

## High-level view

The authoritative package metadata and runtime `__version__` now agree on `0.1.0rc1`; the profile version, signed registry inputs, dependency pins, and geodetic metadata remain unchanged. `MANIFEST.in` and setuptools package data add the notice and runtime schema, while the fresh artifacts are isolated from the historical `dist/` files.

`NOTICE` groups the metadata boundary resources by the recorded source and license, points to the repository source records and API pattern, and avoids asserting copyright ownership or redistribution permission. The candidate remains explicitly non-production, with approval still required for boundary redistribution, the static/candidate geodetic policy, and the retained-boundary package size.

The recorded candidate inspection covers both archive formats, required metadata and resources, boundary hashes, and fail-closed source/archive secret scanning. The evidence also records the current 195-test suite, `twine check`, `pip check`, compile checks, clean wheel/sdist installs, and a final no-upload/no-commit state; the earlier generated-bytecode inventory finding is no longer present.

<details>
<summary>Issues (3)</summary>

1. **Boundary redistribution and NOTICE approval** — **confirmed** human confirmation of redistribution rights for every included boundary file and `NOTICE` accuracy is still required before publication; keep the candidate unpublished until approved.
2. **Static/candidate geodetic status** — **confirmed** approval to distribute the static/candidate profiles as a `0.1.0rc1` technical candidate remains open; retain the non-production labeling and obtain approval before publication.
3. **Candidate package-size approval** — **confirmed** approval of the 17,463,304-byte wheel and 34,610,458-byte sdist while retaining full boundaries remains open; record that decision before publication.

</details>

## Details

### Version authority and isolated distribution inputs

The release-only version declarations are `version = "0.1.0rc1"` in `pyproject.toml` and `__version__ = "0.1.0rc1"` in `src/geosquare_v2/__init__.py`; the plan records that this checkout has no `setup.py` or `setup.cfg`. The candidate artifact metadata and both clean-install smoke tests report the same package and runtime version. The signed registry/profile version remains `2.0.0-rc.2-asean`, so the package release label was not incorrectly applied to signed geodetic data.

`NOTICE` is included through `license-files` and `MANIFEST.in`, and the runtime schema is included both in package data and the sdist manifest. The evidence reports that both formats contain the database/signature pair, schema, boundary resources, source metadata, and `NOTICE`; `registry-trust.json` remains an sdist verification input rather than private-key package data.

### Boundary attribution and publication gates

The notice records the repository-supported groups: Brunei Public Domain; Cambodia, Indonesia, Lao PDR, Malaysia, Singapore, Thailand, and Timor-Leste under the recorded ODbL 1.0 source terms; Myanmar under the recorded CC BY-SA 2.0 terms; the Philippines under the recorded CC BY 3.0 IGO terms; and Viet Nam under the recorded CC BY 4.0 terms. It identifies all 22 metadata full/simplified files and separately identifies the retained `ID.geojson` and `VN.geojson` profile inputs. The source notes, metadata, mirrored packaged notes, and profile source fields are the stated basis; no holder, license text, or redistribution permission is invented.

A **confirmed** publication gate remains open for human confirmation of redistribution rights for every included boundary file and the accuracy of `NOTICE`. The full and simplified resources remain packaged because the signed registry and `verify_boundaries=True` path reference them, so the gate cannot be bypassed by silently removing data. This is an explicitly recorded external approval requirement, not a reason to reject the locally prepared candidate under the task’s verdict rule.

The release documents consistently label the profiles as static/candidate geodetic data and `0.1.0rc1` as a technical candidate, not a production release. A **confirmed** human approval gate remains for distributing that candidate geodetic policy, and publication must remain blocked until it is resolved.

A **confirmed** package-size gate also remains open: the evidence records a 17,463,304-byte wheel and 34,610,458-byte sdist while retaining the full boundaries required by the signed registry. The size decision is explicitly deferred to human approval rather than hidden through data deletion or an invented packaging justification.

### Candidate isolation, secrets, and release lifecycle

The evidence records exactly two fresh outputs under `dist-candidate/`, with the expected `0.1.0rc1` filenames, sizes, and SHA-256 hashes. It records the historical `dist/` sizes and hashes unchanged and confirms that tracked `dist/` artifacts and `.DS_Store` files were neither deleted nor reused; the prior generated-bytecode finding was removed before this review.

The **confirmed** fail-closed scan covered source and release inputs plus archive member names and bytes, with no suspicious filenames, PEM/private-key material, credential patterns, or archive hits. The old compromised key was not used, and the new private key remained outside the repository and artifacts. The **confirmed** lifecycle evidence records no `twine upload`, TestPyPI/PyPI upload, commit, tag, push, or Git-history change.

### Archive and clean-install evidence

The recorded inspection enumerated 59 wheel members and 179 sdist members and asserted the package name, `0.1.0rc1` version, Python `>=3.11`, optional extras, absence of an unconditional runtime dependency, registry database/signature, runtime schema, `NOTICE`, source metadata, and all required full/simplified boundary resources. The boundary hashes were compared with the signed registry/profile references without editing signed artifacts.

The evidence records passing `twine check`, `pip check`, compile checks, and `195 passed` for the current suite. Both clean local artifact installs passed dependency checks and outside-repository smoke tests, including installed version assertions, packaged-resource checks, 11-domain signed-registry loading with `verify_boundaries=True`, and the ID level-9 point-to-cell call. The existing source virtualenv’s stale installed distribution metadata was not used as release evidence; the clean artifact checks provide the relevant installed-package verification.

<details>
<summary>File map</summary>

- `pyproject.toml`, `MANIFEST.in`, and `src/geosquare_v2/__init__.py` — candidate version authority and distribution inclusion.
- `NOTICE` — source-backed boundary attribution and redistribution warning.
- `README.md`, `docs/README.md`, `docs/07_RELEASE_AND_SECURITY.md`, `RELEASE_CANDIDATE.md`, and `CHANGELOG.md` — technical-candidate status, security posture, validation, and no-upload documentation.
- `HANDOVER.md` and `IMPLEMENTATION_PLAN.md` — preserved project history plus release gates and recorded candidate evidence.
- `dist-candidate/geosquare_grid_v2-0.1.0rc1-py3-none-any.whl` and `dist-candidate/geosquare_grid_v2-0.1.0rc1.tar.gz` — fresh isolated candidate artifacts.
- `.agents/tasks/evidence.md` and `.agents/tasks/release-plan.md` — supplied implementation plan and validation record.
- `CELL_DATASET_CONTRACT.md`, schema/implementation files, and implementation tests — intentional pre-existing dataset work preserved during release hardening, not reassessed here.
- Tracked `dist/geosquare_grid_v2-0.1.0-*` and tracked `.DS_Store` files — historical release inputs confirmed preserved.

The full local diff is available with `git diff HEAD` from the `geosquare-grid-v2` checkout.

</details>
