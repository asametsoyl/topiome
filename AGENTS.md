# AGENTS.md — Topiome

> Bu dosya, projeye sonradan katılan **her AI ajanı ve geliştirici** için giriş noktasıdır.
> Kod yazmadan önce bu dosyayı, ardından `docs/STATUS.md` ve `docs/DECISIONS.md` dosyalarını oku.
> İş bitince `docs/STATUS.md` içindeki **Yapılanlar / Sıradaki / Kararlar** bölümlerini güncelle.

---

## 1. Tek cümlede proje

**Topiome**, spatial transcriptomics verisinden hastalığa özgü doku haritaları üreten, çok kiracılı (multi-tenant) bir **Research Use Only (RUO)** SaaS platformudur.

Eski ürün: `glio-cartography` (GBM'e özel, Electron + Python, Teknofest için geliştirildi, yarım kaldı).
Yeni ürün: hastalıktan bağımsız çekirdek + bilimsel olarak doğrulanmış **hastalık paketleri**.

- Çalışma markası: **Topiome** (`topo` = yer/konum, `ome` = bütünlük)
- Alan adı hedefi: `topiome.com` (şu an boş; tescil/hukuk kontrolü yapılacak)
- Konumlandırma: **Research Use Only** — teşhis, prognoz veya tedavi kararı iddiası yok.
- İş modeli: yıllık abonelik (bireysel / laboratuvar / kurumsal) + kurum içi kurulum.

## 2. Değiştirilemez kurallar (non-negotiables)

1. **RUO sınırı.** Ürün hiçbir yerde teşhis, prognoz, tedavi önerisi veya klinik karar desteği olarak sunulmaz. Her raporda ve pazarlama sayfasında görünür RUO uyarısı bulunur.
2. **Veri sahipliği.** Gerçek hasta verisi repo'ya, demo seed'e veya loglara girmez. Örnek veriler sentetik ya da kamuya açık / lisanslı verilerdir.
3. **Benchmark kapısı.** Bir hastalık paketi, `docs/VALIDATION.md` içindeki minimum metrikleri geçmeden "yayında" sayılmaz. Pazarlamada doğruluk iddiası ancak bu kapı geçilince kullanılır.
4. **Belirsizlik görünürlüğü.** Her spot için güven/belirsizlik skoru üretilir; UI ve raporda gösterilir. "Kesin sonuç" dili kullanılmaz.
5. **İzlenebilirlik.** Her analiz; pipeline sürümü, disease pack sürümü, referans veri sürümü, parametreler ve yazılım commit'i ile kaydedilir.
6. **İnsan onayı.** Rapor yayınlama / dışa aktarma adımında kullanıcı onayı ve audit log vardır.

## 3. Mevcut durum

- Aşama: **Faz 1 — çalışan dikey dilim + gerçek Visium/model + üretim altyapısı**
- İlk hedef: 6 veri-zengin hastalık paketi (meme, akciğer, kolorektal, prostat, melanom, GBM) + sentetik demo veriyle uçtan uca akış.
- Gerçek Space Ranger `.h5` / `.mtx` + spatial okuyucu hazır; Wu 2021 meme referansı ve hasta düzeyi GNN domain modeli (beta) bağlı.
- **Bilimsel durum:** Breast ARI 0.260 < 0.35 kapısı, GBM Ivy GAP diagonal −0.179 / top-1 0.0 → **iki paket de beta**, `validated` değil. Ayrıntı: `docs/VALIDATION.md`, `docs/validation/`.
- **Test durumu:** analiz 33, API 34 geçiyor; ruff/ESLint/tsc/`next build` temiz.
- Detaylı yapılanlar/sıradakiler: **`docs/STATUS.md`**
- Ürün tanımı: **`docs/PRODUCT.md`**
- Mimari: **`docs/ARCHITECTURE.md`**
- Doğrulama stratejisi: **`docs/VALIDATION.md`**
- Hastalık paketleri: **`docs/DISEASE_PACKS.md`**

## 4. Hızlı başlangıç

```bash
# Gereksinimler: Node >= 22, uv, Python 3.12 (uv kurar), Docker (opsiyonel)
bash scripts/setup.sh

# Web + API birlikte
npm run dev
# Web: http://localhost:3000
# API: http://localhost:8000/docs
# Demo: demo@topiome.com / demo1234
```

Tek tek:

```bash
npm --prefix apps/web install
npm run dev:web

cd apps/api && uv sync --python 3.12 --extra dev && uv run uvicorn app.main:app --reload --port 8000
```

Kontroller:

```bash
npm test            # analiz + API pytest
npm run lint        # ESLint + ruff
npm run build       # Next.js production build
npm run migrate     # Alembic upgrade head (API açılışta da otomatik çalışır)
```

Üretim kurulumu: `docs/DEPLOY.md` (Docker Compose: Postgres + API + worker + web).

Gerçek veri doğrulaması (veri `data/public` altına indirilir, git'e girmez):

```bash
cd apps/api
uv run python -I ../../scripts/validation/build_reference_wu2021.py      # meme scRNA referansı
uv run --with torch python -I ../../scripts/validation/train_domain_gnn.py  # GNN eğitimi + test
uv run python -I ../../scripts/validation/validate_gbm_gse331374.py      # GBM + Ivy GAP
```

Hasta düzeyindeki eğitim/test ayrımı `scripts/validation/wu2021_common.py` içindedir; test hastaları referans, gen seçimi, epoch seçimi ve kalibrasyonda **asla** kullanılmaz.

## 5. Repo haritası

```
topiome/
├── AGENTS.md                  ← bu dosya; ajanların giriş noktası
├── README.md                  ← kısa tanıtım + kurulum
├── apps/
│   ├── web/                   ← Next.js 16, React 19, Tailwind 4 (marketing + ürün UI)
│   └── api/                   ← FastAPI, SQLAlchemy, auth, upload, run, report API
├── packages/
│   ├── analysis/              ← Python analiz motoru (dekonvolüsyon, GNN, benchmark)
│   └── disease-packs/         ← YAML paketler + şema + sürümlü referanslar (`references/`) + modeller (`models/`)
├── docs/                      ← ürün, mimari, validasyon (held-out raporları `docs/validation/`), marka, güvenlik, yol haritası
├── infra/                     ← Docker Compose, Dockerfile, reverse proxy
├── scripts/                   ← setup, seed, benchmark, veri indirme
├── data/                      ← lokal veri (git'e girmez)
└── tests/                     ← e2e ve entegrasyon testleri
```

## 6. Mimari özet

```
Browser
  │  HTTPS, httpOnly cookie
  ▼
Next.js (apps/web)  ──rewrite /api/*──▶  FastAPI (apps/api)
  │                                        │
  │                                        ├── PostgreSQL / SQLite (metadata)
  │                                        ├── S3 / local storage (raw + derived data)
  │                                        └── job queue (inline dev / DB worker prod)
  │                                                  │
  │                                                  ▼
  │                                        packages/analysis
  │                                        ├── ingest + QC
  │                                        ├── deconvolution (NNLS baseline → Cell2location/Tangram)
  │                                        ├── spatial domains (graph smoothing → GraphST/STAGATE)
  │                                        ├── neighborhood / ligand-receptor
  │                                        ├── drug-target scoring
  │                                        └── report builder (HTML → PDF)
  ▼
Spatial viewer (canvas) + charts + report
```

Detay: `docs/ARCHITECTURE.md`

## 7. Teknoloji kararları

| Katman | Seçim | Neden |
|---|---|---|
| Web | Next.js 16 App Router, TypeScript, Tailwind 4 | Hızlı ürün geliştirme, SEO'lu marketing + app aynı repoda |
| UI | Kendi tasarım sistemi + Radix primitives + lucide | Kontrollü, bilimsel/editoryal görünüm; shadcn kopyaları |
| API | FastAPI + SQLAlchemy 2 + Pydantic 2 | Python analiz ekosistemiyle aynı dil; OpenAPI |
| DB | PostgreSQL (prod), SQLite (dev) | JSONB, audit, çok kiracılı yapı |
| Auth | httpOnly JWT cookie + Argon2 | Basit, sağlam, dış servise bağımlı değil |
| Storage | Local (dev) / S3 uyumlu (prod) | Büyük dosyaları DB'ye koymamak |
| Queue | Inline (dev) / Postgres tabanlı worker (prod) | Uzun analizleri istekten ayırmak; Redis/RQ henüz yok |
| Analiz | NumPy/SciPy/scikit-learn baseline; ağır modeller opsiyonel extra | Hızlı kurulum; torch/scanpy her ortamda gerekmesin |
| Deployment | Docker Compose → tek VM; sonra AWS/Fly.io | Erken aşamada düşük maliyet |

## 8. Geliştirme kuralları

- **Dil:** Ürün UI'ı İngilizce (global), ekip dokümanları Türkçe. Kod, değişken, commit mesajları İngilizce.
- **Commit:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- **Python:** 3.12, ruff + pytest, type hints zorunlu, `uv` kullan.
- **TypeScript:** strict mode, `any` yasak (kaçınılmazsa gerekçeli), server/client ayrımına dikkat.
- **API:** Tüm yanıtlar `snake_case`; tarihler ISO-8601 UTC; hatalar `{ "detail": "..." }`.
- **UI:** Boşluklar 4'ün katı; köşe yarıçapı 12–16px; gölge yerine kenarlık; koyu tema varsayılan.
- **Test:** Yeni iş = en az bir test. Analiz kodu = benchmark fixture'ı.
- **Dosya adları:** `kebab-case` (TS), `snake_case` (Python).
- **Sırlar:** `.env` commit edilmez. Örnek değerler `.env.example` içinde.

## 9. Veri ve model ilkeleri

- Eski sürümdeki düşük doğruluk, tek model + yetersiz veri + validasyonsuz GNN'den kaynaklandı. Yeni yaklaşım:
  1. **Önce veri:** kamuya açık, lisansı uygun, hasta sayısı ve spot sayısı yüksek veri setleri.
  2. **Baseline önce:** NNLS / marker-score baseline çalışmadan GNN'e geçilmez.
  3. **Ensemble + uncertainty:** en az iki dekonvolüsyon yöntemi; spot bazında belirsizlik.
  4. **Held-out validation:** aynı hastadan değil, ayrı çalışmalardan test.
  5. **Model card:** her sürüm için veri, metrik, sınırlama, kullanım amacı.
- Disease pack'ler `packages/disease-packs/*.yaml`; şema `schema.json`; doğrulama `scripts/validate_packs.py`.

## 10. Ajan çalışma protokolü

1. `AGENTS.md` → `docs/STATUS.md` → ilgili dokümanı oku.
2. Yeni karar gerekiyorsa `docs/DECISIONS.md`'ye ADR ekle; sessizce mimari değiştirme.
3. Küçük, çalışan, test edilmiş dilimler halinde ilerle. Büyük refactor'ları ayrı oturuma bırak.
4. Her oturum sonunda:
   - `docs/STATUS.md` → "Yapılanlar" işaretle, "Sıradaki" güncelle, "Oturum kaydı" ekle.
   - `docs/CHANGELOG.md` → kullanıcıya görünen değişiklikleri yaz.
5. Çalıştırmadığın komutu/testi "çalışıyor" diye işaretleme. `npm run build`, `uv run pytest` ve mümkünse `curl` smoke test'lerini çalıştır.
6. Gerçek hasta verisi, API anahtarı veya kişisel veri isteme/yazma.

## 11. Bilinen kısıtlar

- Proje **exFAT** diskte (`/Volumes/SAMSUNG/topiome`). Symlink çalışıyor; ancak dosya sistemi yavaş. `node_modules` ve `.venv` büyükse lokal APFS'e taşımayı düşün (symlink ile).
- Python 3.14 sistemde var; bilimsel paketler için **3.12** kullan (`uv`).
- Ağır analiz bağımlılıkları (`torch`, `scanpy`, `tangram`, `cell2location`) varsayılan kurulumda yok; `pip install -e ".[full]"` ile gelir.
- Stripe, SMTP ve S3 prod ayarları henüz bağlı değil; arayüzler hazır, gerçek anahtar yok. Kuyruk Postgres tabanlıdır; Redis/RQ ve otomatik retry yok.
- Bilimsel kapılar: **breast ARI 0.260 < 0.35**, **GBM Ivy GAP diagonal −0.179 / top-1 0.0**. İki paket de beta; "validated" veya klinik doğruluk iddiası yok.
- Marka tescili ve domain satın alımı yapılmadı; `Topiome` çalışma adıdır.
- exFAT'ta macOS her dosyanın yanına `._*` yazar: Turbopack dosya önbelleği kapalıdır (ADR-015); migration'ları bare `alembic` ile değil `cd apps/api && uv run python -m app.migrate …` ile çalıştır (ADR-011). Docker build de `._*` xattr'ında kırılır; temiz kopya kullan (`docs/DEPLOY.md`).
- Next.js `rewrites` hedefi (`API_URL`) `next build` anında sabitlenir; farklı portta API için yeniden derle ya da `next dev` kullan.
- Eski ürün kodu: `~/Downloads/glio-cartography-main` (GitHub `main` indirmesi). Nelerin taşındığı/taşınmadığı: `docs/DECISIONS.md` ADR-014.

## 12. Bağlantılar

- Eski repo: https://github.com/asametsoyl/glio-cartography
- Eski site: https://gliocartography.com
- Yeni marka hedefi: `topiome.com` (alınacak)
- Ekip iletişimi: repo issue'ları + `docs/STATUS.md`

---

_Son güncelleme: 2026-11-06 · Faz 1 + gerçek Visium/model + üretim worker/Docker_
