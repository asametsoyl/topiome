# API — Topiome v1

Base URL: `http://localhost:8000/api/v1` (dev) · `https://api.topiome.com/api/v1` (prod)
Auth: `topiome_session` httpOnly cookie (web) veya `Authorization: Bearer <api_key>` (Faz 2).

## 1. Genel kurallar

- Tüm yanıtlar JSON; tarihler ISO-8601 UTC.
- Hata formatı: `{ "detail": "message", "code": "ERROR_CODE", "trace_id": "..." }`
- Sayfalama: `?limit=50&offset=0`; yanıt `{ items, total, limit, offset }`.
- Idempotency: `POST /runs` için `Idempotency-Key` opsiyonel.
- Rate limit: giriş denemeleri IP + e-posta başına 15 dk / 10, IP başına 50 başarısız; `429` + `Retry-After`. Genel `X-RateLimit-*` başlıkları henüz yok.

## 2. Auth

| Method | Path | Açıklama |
|---|---|---|
| POST | `/auth/register` | `{name, email, password, org_name}` → user + org |
| POST | `/auth/login` | `{email, password}` → cookie |
| POST | `/auth/logout` | cookie sil |
| GET | `/auth/me` | kullanıcı + org + rol |
| POST | `/auth/demo` | demo hesabına giriş (feature flag) |
| POST | `/auth/forgot-password` | e-posta gönder (Faz 2) |
| POST | `/auth/reset-password` | token ile sıfırla (Faz 2) |

## 3. Organizasyon

| Method | Path | Açıklama |
|---|---|---|
| GET | `/org` | mevcut org |
| PATCH | `/org` | ad, slug, ayarlar |
| GET | `/org/members` | üyeler |
| POST | `/org/invitations` | davet |
| DELETE | `/org/members/{id}` | üye çıkar |
| GET | `/org/audit-logs` | audit kayıtları |

## 4. Hastalık paketleri

| Method | Path | Açıklama |
|---|---|---|
| GET | `/disease-packs` | liste (`?status=validated`) |
| GET | `/disease-packs/{slug}` | detay + marker/zone/hedef |
| GET | `/disease-packs/{slug}/validation` | benchmark metrikleri |

## 5. Projeler

| Method | Path | Açıklama |
|---|---|---|
| GET | `/projects` | liste |
| POST | `/projects` | `{name, description, disease_pack}` |
| GET | `/projects/{id}` | detay + sample/run özeti |
| PATCH | `/projects/{id}` | güncelle |
| DELETE | `/projects/{id}` | soft delete |

## 6. Örnekler

| Method | Path | Açıklama |
|---|---|---|
| GET | `/projects/{id}/samples` | liste |
| POST | `/projects/{id}/samples` | multipart: metadata + dosyalar |
| GET | `/samples/{id}` | detay + QC özeti |
| DELETE | `/samples/{id}` | soft delete |
| GET | `/samples/{id}/files` | dosya listesi + signed URL |

Yükleme biçimleri: `filtered_feature_bc_matrix.h5`; veya `matrix.mtx(.gz)` + `barcodes.tsv(.gz)` + `features.tsv(.gz)`/`genes.tsv(.gz)` + `tissue_positions.csv` / `tissue_positions_list.csv`; `.zip` / `.tar` / `.tar.gz` / `.tgz` arşivi. Opsiyonel `scalefactors_json.json` ve doku görüntüsü. Dosya göndermeden yalnız `metadata` ile sentetik demo örneği oluşturulabilir.

`POST /auth/demo` üretimde `ALLOW_DEMO_LOGIN=false` ise 404 döner.

## 7. Çalıştırmalar

| Method | Path | Açıklama |
|---|---|---|
| POST | `/samples/{id}/runs` | `{disease_pack, params}` → run |
| GET | `/runs` | liste (`?status=`) |
| GET | `/runs/{id}` | durum + aşama + hata |
| POST | `/runs/{id}/cancel` | iptal |
| POST | `/runs/{id}/retry` | yeniden dene |
| GET | `/runs/{id}/results` | özet sonuçlar |
| GET | `/runs/compare?a=&b=` | iki başarılı run'ı yan yana (kayıtlı sonuçtan; yeniden analiz yok). Başka org → 404, bitmemiş run → 409, aynı run → 400; paket/sürüm farkında `warnings` |
| GET | `/runs/{id}/artifacts` | dosya listesi |
| GET | `/runs/{id}/report` | HTML rapor |
| POST | `/runs/{id}/report/pdf` | PDF üret (Faz 2) |

## 8. Dashboard

| Method | Path | Açıklama |
|---|---|---|
| GET | `/dashboard/summary` | proje/örnek/run sayıları, son aktiviteler |
| GET | `/dashboard/activity` | son 20 olay |

## 9. Faturalama (Faz 2)

| Method | Path | Açıklama |
|---|---|---|
| GET | `/billing/plans` | planlar |
| GET | `/billing/subscription` | mevcut abonelik |
| POST | `/billing/checkout` | Stripe checkout session |
| POST | `/billing/webhook` | Stripe webhook (imzalı) |

## 10. Sağlık

| Method | Path | Açıklama |
|---|---|---|
| GET | `/health` | `{status, version, db, storage}` |
| GET | `/version` | sürüm bilgisi |

## 11. Örnek akış

```bash
# login
curl -c cookies.txt -X POST localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"demo@topiome.com","password":"demo1234"}'

# proje oluştur
curl -b cookies.txt -X POST localhost:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"Breast pilot","disease_pack":"breast"}'

# örnek yükle
curl -b cookies.txt -X POST localhost:8000/api/v1/projects/1/samples \
  -F 'metadata={"sample_id":"S001","disease":"breast"}' \
  -F 'files=@matrix.mtx.gz'

# çalıştır
curl -b cookies.txt -X POST localhost:8000/api/v1/samples/1/runs \
  -H 'Content-Type: application/json' \
  -d '{"disease_pack":"breast","params":{"min_spots":500}}'

# sonuç
curl -b cookies.txt localhost:8000/api/v1/runs/1/results
```

## 12. OpenAPI

Çalışan API: `http://localhost:8000/docs` · şema: `/openapi.json`.
