# Disease Packs

Hastalığa özgü marker, bölge, hedef ve rapor tanımları. Kod değil, **veri**.

## Paketler

| Dosya | ID | Durum | Veri zenginliği |
|---|---|---|---|
| `breast.yaml` | breast | beta | high |
| `colorectal.yaml` | colorectal | beta | high |
| `lung.yaml` | lung | draft | high |
| `melanoma.yaml` | melanoma | draft | medium |
| `prostate.yaml` | prostate | draft | medium |
| `glioblastoma.yaml` | glioblastoma | beta | medium |

## Doğrulama

```bash
cd apps/api
uv run python -m app.validate_packs
```

Şema: `schema.json` (JSON Schema draft-07).

## Yeni paket ekleme

1. `docs/DISEASE_PACKS.md` sürecini oku.
2. YAML'ı kopyala, `id`/`version`/`status` güncelle.
3. Marker ve zone'ları literatürle doğrula.
4. `references.yaml`'a kaynak ekle (planlanan).
5. Benchmark çalıştır, metrikleri `validation.metrics`'e yaz.
6. Uzman onayı olmadan `validated` yapma.

## Not

Bu paketler **Research Use Only**'dir. Bölge etiketleri patolojik tanı değil, araştırma amaçlı mekânsal domain'lerdir.
