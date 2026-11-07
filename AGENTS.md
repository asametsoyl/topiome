# AGENTS.md — Topiome

> Bu dosya, projeye sonradan katılan **her AI ajanı ve geliştirici** için giriş noktasıdır.
> Kod yazmadan önce bu dosyayı, ardından `docs/STATUS.md` ve `docs/DECISIONS.md` dosyalarını oku.
> İş bitince `docs/STATUS.md` içindeki **Yapılanlar / Sıradaki / Kararlar** bölümlerini güncelle.

---

## 1. Tek cümlede proje

**Topiome**, tanımlı perturbasyonlara tek hücre yanıtlarını tahmin etmeyi araştıran bir yazılım projesidir (**Research Use Only, RUO**).

Eski ürünler: `glio-cartography` ve spatial-transkriptomik Topiome. Kodları ve küçük validasyon raporları legacy olarak korunuyor; yerel spatial veri 2026-11-07'de temizlendi.
Yeni yön: görülmemiş perturbasyon ve hücre bağlamlarında yanıt tahmini. İlk H1 aggregate baseline deneyi var; Topiome modeli ve held-out context sonucu yok.

- Çalışma markası: **Topiome** (`topo` = yer/konum, `ome` = bütünlük)
- Alan adı hedefi: `topiome.com` (şu an boş; tescil/hukuk kontrolü yapılacak)
- Konumlandırma: **Research Use Only** — teşhis, prognoz veya tedavi kararı iddiası yok.
- İş modeli: belirlenmedi; bilimsel fizibilite ve alıcı ihtiyacı görülmeden fiyatlandırma yapılmaz.

## 2. Değiştirilemez kurallar (non-negotiables)

1. **RUO sınırı.** Ürün hiçbir yerde teşhis, prognoz, tedavi önerisi veya klinik karar desteği olarak sunulmaz. Her raporda ve pazarlama sayfasında görünür RUO uyarısı bulunur.
2. **Veri sahipliği.** Gerçek hasta verisi repo'ya, demo seed'e veya loglara girmez. Örnek veriler sentetik ya da kamuya açık / lisanslı verilerdir.
3. **Benchmark kapısı.** Yeni model, `docs/VALIDATION.md` içindeki perturbasyon ve bağlam düzeyindeki held-out kapıları geçmeden başarı iddiası alamaz.
4. **Belirsizlik görünürlüğü.** Her tahmin için destek, belirsizlik ve kapsam dışı koşullar gösterilir. "Kesin sonuç" dili kullanılmaz.
5. **İzlenebilirlik.** Her analiz; model/pipeline sürümü, kaynak/lisans, veri hash'i, split, parametreler ve yazılım commit'i ile kaydedilir.
6. **İnsan onayı.** Rapor yayınlama / dışa aktarma adımında kullanıcı onayı ve audit log vardır.

## 3. Mevcut durum (2026-11-07)

- Aşama: perturbasyon yanıtı araştırma fizibilitesi.
- Topiome adı korunuyor; yeni kayıt ve ücretli ürün erişimi kapalı.
- Yeni yönde Topiome modeli eğitilmedi; bir public aggregate dataset ve baselinelar üzerinde keşifsel sonuç var, bağımsız deney yok.
- Eski spatial app ve kodu legacy. Yerel yaklaşık 9.2 GB public/processed spatial dosya temizlendi.
- Detaylar: `docs/STATUS.md`, `docs/PRODUCT.md`, `docs/VALIDATION.md`, `docs/DATA.md`.

## 4. Hızlı başlangıç

```bash
# Gereksinimler: Node >= 22, uv, Python 3.12 (uv kurar), Docker (opsiyonel)
bash scripts/setup.sh

# Web + API birlikte
npm run dev
# Web: http://localhost:3000
# API: http://localhost:8000/docs
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

Eski spatial kod ve doğrulama raporları `docs/legacy/spatial/` altında tutulur. İlk perturbasyon baseline komutu `python scripts/perturbation/benchmark_vcc_pie_baselines.py`; sonuç tek hücre hattındaki aggregate ölçümle sınırlıdır. Eski `scripts/validation/` komutları yeni yönü doğrulamaz.

## 5. Repo haritası

```
topiome/
├── AGENTS.md                  ← bu dosya; ajanların giriş noktası
├── README.md                  ← kısa tanıtım + kurulum
├── apps/
│   ├── web/                   ← Next.js 16, React 19, Tailwind 4 (marketing + ürün UI)
│   └── api/                   ← FastAPI, SQLAlchemy, auth, upload, run, report API
├── packages/
│   ├── analysis/              ← legacy spatial analiz motoru; perturbasyon modeli henüz yok
│   └── disease-packs/         ← legacy spatial paketleri
├── docs/                      ← aktif araştırma planı + `docs/legacy/spatial/` arşivi
├── infra/                     ← Docker Compose, Dockerfile, reverse proxy
├── scripts/                   ← setup, seed, benchmark, veri indirme
├── data/                      ← `data/perturbation/` yerel verisi (git'e girmez)
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
  │                                        Gelecek araştırma akışı (henüz uygulanmadı):
  │                                        ├── perturbasyon verisi + kontrol eşleştirme
  │                                        ├── perturbation/context-held-out split
  │                                        ├── baselines → yayınlanmış yöntemlerle kıyas
  │                                        └── metrik, belirsizlik ve provenance raporu
  ▼
Research preview website; eski spatial workspace legacy
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
- **UI:** Boşluklar 4'ün katı; köşe yarıçapı 12–16px; gölge yerine kenarlık; araştırma önizlemesi açık/paper temalı.
- **Test:** Yeni iş = en az bir test. Analiz kodu = benchmark fixture'ı.
- **Dosya adları:** `kebab-case` (TS), `snake_case` (Python).
- **Sırlar:** `.env` commit edilmez. Örnek değerler `.env.example` içinde.

## 9. Veri ve model ilkeleri

1. Her public veri bileşeni için kaynak, lisans/izin, indirme tarihi, hash ve assay/bağlam metadata'sı kaydedilir. Atlas toplam hücre sayısı kullanılabilir benchmark örneği gibi sunulmaz.
2. Perturbasyon, kontrol, örnek/batch ve hücre bağlamı eşleştirilmeden model girdisi oluşturulmaz.
3. Önce no-change, kontrol/bağlam ortalaması ve basit doğrusal baseline'lar kurulur; karmaşık model bunları geçmeden eklenmez.
4. Bölme hücre seviyesinde rastgele yapılmaz. Görülmemiş perturbasyon ve biyolojik bağlam testleri ayrı raporlanır; deney/batch sızıntısı denetlenir.
5. Belirsizlik, başarısız bağlamlar ve kapsam dışı koşullar gösterilir. Public benchmark, prospektif deney veya klinik fayda kanıtı değildir.
6. Veri/model kartı; kaynak, lisans, split, metrik, sınırlama, pipeline sürümü ve commit'i içerir.

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
- Yeni yönde öğrenilmiş Topiome modeli veya bağımsız deney yok. Mevcut H1 aggregate baseline keşifseldir; genelleme/ürün başarısı iddiası değildir.
- Eski spatial verilerden yaklaşık 9.2 GB temizlendi. Tarihsel raporlar `docs/legacy/spatial/validation/` içinde; eski spatial sonuçlar yeni yönü desteklemez.
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

_Son güncelleme: 2026-11-07 · Perturbasyon yanıtı araştırma fizibilitesi; model henüz yok_
