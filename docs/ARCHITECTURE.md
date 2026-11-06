# Mimari — Topiome

## 1. Genel bakış

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Browser (React 19)                         │
│  Marketing  │  Auth  │  Dashboard  │  Spatial viewer  │  Reports   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS, httpOnly session cookie
┌───────────────────────────────▼─────────────────────────────────────┐
│                    Next.js 16 (apps/web)                            │
│  App Router · server components · route handlers · rewrites         │
│  /api/*  ──────────────── proxy ────────────────▶ FastAPI           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                    FastAPI (apps/api)                               │
│  Auth · Orgs · Projects · Samples · Runs · Results · Reports        │
│  SQLAlchemy 2 · Pydantic 2 · Alembic · Argon2 · JWT cookie          │
└───────┬───────────────────────┬───────────────────────┬─────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌────────────────┐      ┌─────────────────────┐
│ PostgreSQL    │      │ S3 / local FS  │      │ Queue               │
│ (metadata)    │      │ (raw/derived)  │      │ inline dev / DB worker prod│
└───────────────┘      └────────────────┘      └──────────┬──────────┘
                                                            │
                                                ┌───────────▼──────────┐
                                                │ packages/analysis    │
                                                │ ingest → QC →        │
                                                │ deconv → domains →   │
                                                │ niches → targets →   │
                                                │ report               │
                                                └──────────────────────┘
```

## 2. Neden bu mimari?

- **Web SaaS** seçildi: çok kiracılı, uzaktan erişim, kolay güncelleme, abonelik.
- **Next.js + FastAPI ayrımı:** UI/SEO için Next.js; analiz ve bilimsel ekosistem için Python. Aynı dilde zorlamak yerine doğru araç.
- **Ayrı analysis paketi:** API'den bağımsız test edilebilir, CLI/benchmark ve worker tarafından aynı kod kullanılır.
- **Disease packs veri olarak:** Yeni hastalık eklemek kod değişikliği değil, YAML + doğrulama + benchmark işidir.
- **Storage soyutlaması:** Lokal geliştirme ile S3 prod arasında geçiş; büyük dosyalar DB'ye girmez.

## 3. Monorepo

| Yol | Sorumluluk |
|---|---|
| `apps/web` | Marketing, auth, dashboard, viewer, rapor UI |
| `apps/api` | REST API, auth, DB, upload, job tetikleme, rapor üretimi |
| `packages/analysis` | Saf Python analiz kütüphanesi + CLI |
| `packages/disease-packs` | YAML paketler, JSON şema, doğrulama |
| `infra` | Docker Compose, Dockerfile, Caddy |
| `scripts` | Setup, seed, benchmark, veri indirme |
| `tests` | E2E, entegrasyon, fixture'lar |

## 4. Veri modeli (özet)

```
User ──< Membership >── Organization ──< Project ──< Sample ──< Run ──< Result
                                                          │         │
                                                          │         └──< Report
                                                          └──< Artifact (raw/derived)
Organization ──< Invitation
Organization ──< Subscription
User ──< ApiKey
Organization ──< AuditLog
```

- **Organization:** kiracı; tüm veriler org_id ile izole.
- **Project:** bir çalışma/hipotez; hastalık paketi seçilir.
- **Sample:** bir doku kesiti; metadata + dosyalar.
- **Run:** bir pipeline çalıştırması; pack sürümü, parametreler, durum.
- **Result:** JSONB özet + dosya referansları (spatial coordinates, scores, clusters).
- **Report:** HTML/PDF snapshot; üretildiği andaki sürümlerle.

## 5. Auth ve yetkilendirme

- E-posta + şifre; Argon2id hash.
- JWT, `httpOnly`, `Secure` (prod), `SameSite=Lax` cookie.
- Roller: `owner` > `admin` > `analyst` > `viewer`.
- Her istekte `org_id` üyeliği doğrulanır; kaynak sahipliği kontrol edilir.
- API anahtarları: hash'lenmiş, scope'lu, iptal edilebilir.
- Rate limit: auth endpoint'leri için IP + e-posta bazlı.
- CSRF: SameSite cookie + `Origin` kontrolü; state-changing isteklerde.

## 6. Dosya yükleme

- Desteklenen (Faz 1): Space Ranger `filtered_feature_bc_matrix.h5`; veya `matrix.mtx(.gz)` + `barcodes.tsv(.gz)` + `features.tsv(.gz)`/`genes.tsv(.gz)` + `tissue_positions.csv` / `tissue_positions_list.csv`; opsiyonel `scalefactors_json.json` ve doku görüntüsü.
- Alternatif: `.zip`, `.tar`, `.tar.gz`, `.tgz` (path traversal korumalı çıkarma); `.h5` doğrudan yükleme.
- QC tam matris üzerinde hesaplanır; gen ön seçimi kütüphane boyutunu değiştirmez.
- Doğrulama: boyut, MIME, zorunlu dosyalar, barcode tutarlılığı, spot sayısı.
- Depolama yolu: `orgs/{org_id}/projects/{project_id}/samples/{sample_id}/raw/...`
- Metadata: `sample.json` (tür, doku, hastalık, platform, hazırlık, batch).
- Virüs taraması prod'da zorunlu (ClamAV sidecar veya S3 malware scan).

## 7. Job akışı

1. `POST /runs` → Run kaydı `queued`.
2. Dev: FastAPI `BackgroundTasks` ile inline; Prod: run `queued` kalır, `python -m app.worker` atomik olarak sahiplenir (Postgres tabanlı kuyruk; Redis/RQ henüz yok).
3. Worker: dosyaları indirir → pipeline → sonuçları yazar → Run `succeeded/failed`.
4. UI polling (`/runs/{id}`) veya SSE (sonra).
5. Hata: `error_code`, `error_message`, `trace_id`; kullanıcıya anlaşılır mesaj.
6. İdempotency: aynı sample + pack + params için hash; tekrar çalıştırma uyarısı.

## 8. Analiz pipeline (Faz 1 baseline)

```
load → validate → QC → normalize → deconvolve (NNLS) → spatial smooth
     → domain clustering → neighborhood → target score → uncertainty → artifacts
```

- **QC:** toplam UMI, gen sayısı, mito oranı, spot yoğunluğu; eşik dışı spotlar işaretlenir (silinmez).
- **Normalize:** CPM/median-of-ratios; log1p.
- **Deconvolve:** referans hücre tipi imzalarına karşı NNLS; her spot için ağırlıklar.
- **Spatial smooth:** kNN grafiği üzerinde ağırlıklı ortalama; sınır koruma.
- **Domains:** ölçeklenmiş özellikler + koordinatlar üzerinde KMeans/Leiden (sentetik) veya paketle gelen GraphSAGE domain modeli (gerçek örnek, uygun gen kapsamı); klinik olmayan "domain" etiketi.
- **Gerçek örnek referansı:** paket `reference.signatures` tanımlıysa NNLS bu sürümlü scRNA imzalarına karşı çalışır; sentetik demo marker pseudosignature kullanır.
- **Atlas kontrolü:** paket `atlas_reference` tanımlıysa (şu an GBM/Ivy GAP) zon ortalamaları dış atlasla z-skor korelasyonuna sokulur; marker genleri hariç tutulur.
- **Neighborhood:** hücre tipi komşuluk zenginleşmesi; ligand-receptor için hazırlık.
- **Target score:** disease pack'teki hedef genlerin hücre tipi/bölge ifadesi; skor + belirsizlik.
- **Uncertainty:** bootstrap yeniden örnekleme veya posterior benzeri entropi; spot bazında 0–1.
- **Artifacts:** `spots.json`, `domains.json`, `composition.json`, `qc.json`, `report.html`.

Ağır modeller (Cell2location, Tangram, GraphST, STAGATE) aynı arayüze adaptör olarak eklenir; varsayılan kurulumda gelmez.

## 9. Raporlama

- HTML (Jinja2) → yazdırma/PDF.
- Bölümler: özet, veri ve yöntem, QC, hücre kompozisyonu, spatial domains, hedef skorları, belirsizlik, sınırlamalar, sürümler, RUO.
- Her rapor snapshot: pack sürümü, pipeline sürümü, parametre hash'i, referans veri sürümü.
- Rapor üretimi audit log'a yazılır.

## 10. Deployment

### Dev
- SQLite + local storage + inline queue.
- `npm run dev` (web + api).

### Prod (ilk)
- Tek VM: Docker Compose (web, api, worker, postgres; TLS için önüne Caddy/Traefik). S3 uyumlu depolama ve Redis/RQ ileride.
- Caddy: otomatik TLS, reverse proxy.
- Yedek: günlük Postgres dump + S3 versiyonlama.
- Gözlem: structured JSON log, Sentry (opsiyonel), uptime kontrolü.

### Ölçek
- API ve worker ayrı ölçeklenir; Postgres yönetilen servise taşınır; S3 + CDN.
- Çok bölgeli değil; önce tek bölge (AB/Frankfurt) — KVKK/GDPR için veri ikametgahı.

## 11. Güvenlik özeti

Detay: `docs/SECURITY.md`.

- Tüm veriler org_id ile izole.
- Prod'da TLS zorunlu; HSTS.
- Secret'lar environment/secret manager; repo'da yok.
- Yüklenen dosyalar signed URL ile; doğrudan public bucket yok.
- Audit log: giriş, yükleme, çalıştırma, rapor, silme, üye değişikliği.
- Veri saklama: varsayılan 24 ay; org politikasıyla değiştirilebilir; silme talebi 30 gün içinde.
- Yedekler şifreli; erişim çift faktörlü.

## 12. ADR özeti

| # | Karar | Durum |
|---|---|---|
| ADR-001 | Web SaaS + Python motoru | Kabul |
| ADR-002 | Hastalıktan bağımsız çekirdek + YAML disease packs | Kabul |
| ADR-003 | RUO konumlandırma | Kabul |
| ADR-004 | FastAPI + SQLAlchemy, Next.js ayrı | Kabul |
| ADR-005 | Faz 1'de NNLS baseline; ağır model opsiyonel | Kabul |
| ADR-006 | SQLite dev / Postgres prod | Kabul |
| ADR-007 | exFAT diskte geliştirme; gerekirse node_modules symlink | Kabul |

Detay ve gerekçeler: `docs/DECISIONS.md`.
