# Registry SQLite — Ringkasan & Cara Pakai

Dokumen ini menjelaskan dengan bahasa sederhana apa yang berubah dari sistem registry lama (file JSON) ke sistem baru (database SQLite), serta cara pakai dan cara mengelolanya sehari-hari.

## Apa yang berubah

Dulu, data registry (manifest, profil domain, dan metadata skala) disimpan tersebar di banyak file JSON:

```
src/geosquare_v2/data/registry/
  registry.v2.json
  registry.unsigned.v2.json
  profiles/ID.v2.json
  profiles/VN.v2.json
  scale/ID_GRID_V2.json
  scale/VN_GRID_V2.json
```

Sekarang, semua data itu (manifest + profil domain + metadata skala) digabung jadi satu file database SQLite:

```
src/geosquare_v2/db/registry.db       <- databasenya
src/geosquare_v2/db/registry.db.sig   <- tanda tangan digital untuk database ini
```

File JSON yang lama sudah dihapus. Yang **tidak berubah**: file boundary (`boundaries/ID.geojson`, `boundaries/VN.geojson`) tetap ada sebagai file biasa, tidak dipindah ke database (karena isinya data geometri besar, lebih cocok tetap jadi file).

## Kenapa pakai signature terpisah, bukan seperti JSON dulu

Dulu, tanda tangan (signature) ditempel langsung di dalam file JSON manifest. Sekarang karena `.db` adalah file biner (bukan JSON), tanda tangannya dibuat terpisah:

1. Hitung hash SHA-256 dari seluruh isi file `registry.db`.
2. Tanda tangani hash itu dengan private key (Ed25519) — sama seperti key yang dipakai untuk JSON dulu.
3. Simpan hasilnya di file kecil `registry.db.sig` (isinya cuma: algoritma, key_id, signature, dan hash-nya).

Jadi setiap ada `registry.db`, harus ada `registry.db.sig` di sebelahnya. Kalau salah satu tidak ada, atau isi `.db` berubah sedikit saja, loader akan menolak memuatnya (fail-closed, tidak asal jalan).

## Hal-hal baru yang ditambahkan

| File/Folder | Fungsi |
|---|---|
| `src/geosquare_v2/db.py` | Isinya: skema tabel SQLite, `MigrationTool` (untuk konversi JSON → database), dan `DbRegistryLoader` (untuk memuat & verifikasi database saat aplikasi jalan) |
| `scripts/migrate_registry_to_db.py` | Script untuk konversi data JSON lama jadi `registry.db` |
| `scripts/sign_registry_db.py` | Script untuk menandatangani `registry.db` menjadi `registry.db.sig` |
| `scripts/generate_release_candidates.py` | Sudah diperbarui: sekarang langsung menghasilkan `registry.db` (bukan file JSON lagi) |
| `src/geosquare_v2/db/registry.db` & `registry.db.sig` | Database registry yang sudah jadi dan sudah ditandatangani, siap dipakai |

Kelas `DomainRegistry` dan `ReleaseProfile` (tempat data profil disimpan di memory) **tidak berubah sama sekali** — jadi kode yang sudah ada sebelumnya tetap bisa jalan seperti biasa, cuma cara memuatnya (loader) yang beda.

## Cara pakai (baca data registry di kode)

```python
import base64, json
from pathlib import Path
from geosquare_v2.db import DbRegistryLoader

project_root = Path(".")
encoded_keys = json.loads((project_root / "registry-trust.json").read_text())
trust = {key_id: base64.b64decode(value) for key_id, value in encoded_keys.items()}

registry = DbRegistryLoader(
    trust,                                                       # public key yang dipercaya
    project_root / "src/geosquare_v2/db",                                    # folder tempat registry.db & .sig
    boundary_root=project_root / "src/geosquare_v2/data/registry",  # lokasi file boundary
).load()

profile = registry.get("ID")   # atau registry.get("VN")
```

Kalau signature tidak valid, key tidak dipercaya, atau ada file yang hilang/rusak — `load()` akan langsung melempar error, tidak akan mengembalikan data setengah-setengah.

## Cara mengelola (bikin/update database baru)

Dipakai kalau ada perubahan profil, boundary, CRS, atau metadata skala:

```zsh
# 1. Generate ulang kandidat database (belum ditandatangani)
.venv/bin/python scripts/generate_release_candidates.py

# 2. Review dulu isi database (opsional, cek pakai sqlite3)
sqlite3 src/geosquare_v2/db/registry.db ".dump"

# 3. Tandatangani dengan private key (private key JANGAN pernah di-commit)
.venv/bin/python scripts/sign_registry_db.py \
  --private-key /secure/path/geosquare-registry-private.pem \
  --db src/geosquare_v2/db/registry.db \
  --output src/geosquare_v2/db/registry.db.sig \
  --key-id geosquare-registry-2026-09
```

Kalau cuma perlu migrasi manual dari folder JSON lama (misal untuk testing atau proses lain):

```zsh
.venv/bin/python scripts/migrate_registry_to_db.py \
  --source src/geosquare_v2/data/registry \
  --destination src/geosquare_v2/db/registry.db
```

## Yang perlu diingat

- **Jangan edit `registry.db` secara manual.** Selalu generate ulang lewat script, lalu tandatangani ulang. Kalau file database diubah manual, signature-nya jadi tidak valid dan loader akan menolaknya.
- **Private key jangan pernah masuk git**, chat, atau folder rilis. Simpan di tempat aman terpisah.
- Setiap kali `registry.db` diganti, `registry.db.sig` **harus** dibuat ulang juga. Keduanya sepasang.
- File boundary (`*.geojson`) tetap dikelola seperti biasa, tidak ada perubahan cara kerja di sana.
- Kalau butuh cek isi database secara manual, pakai `sqlite3 src/geosquare_v2/db/registry.db` lalu jalankan query SQL biasa (misalnya `SELECT * FROM domains;`).

## Testing

Semua perubahan ini sudah ditutup dengan test (43 test, semua lolos):

```zsh
.venv/bin/pytest -q
```

Test-nya mencakup: migrasi berhasil/gagal, verifikasi signature (termasuk kalau ada yang di-tamper), hash boundary yang salah, sampai perbandingan hasil data lama (JSON) vs baru (SQLite) supaya dipastikan datanya sama persis.
